#!/usr/bin/env python3
"""
Machine Learning-based Anomaly Detection for SIEM
Uses Isolation Forest and One-Class SVM
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import numpy as np
import pickle
from typing import Dict, Any, List
from datetime import datetime
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import logging

logger = logging.getLogger(__name__)


class MLAnomalyDetector:
    """Machine Learning-based anomaly detector"""
    
    def __init__(self, model_type='isolation_forest', contamination=0.1):
        self.model_type = model_type
        self.contamination = contamination
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=10)
        self.model = None
        self.is_trained = False
        self.feature_names = []
        self.training_data = []
        
        self._initialize_model()
        logger.info(f"ML Anomaly Detector initialized ({model_type})")
    
    def _initialize_model(self):
        """Initialize ML model"""
        if self.model_type == 'isolation_forest':
            self.model = IsolationForest(
                contamination=self.contamination,
                random_state=42,
                n_estimators=100,
                max_samples='auto',
                max_features=1.0
            )
        elif self.model_type == 'one_class_svm':
            self.model = OneClassSVM(
                kernel='rbf',
                gamma='auto',
                nu=self.contamination
            )
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
    
    def extract_features(self, event: Dict[str, Any]) -> np.ndarray:
        """Extract numerical features from event"""
        features = []
        
        # Numerical features
        features.append(event.get('failed_logins', 0))
        features.append(event.get('bytes_sent', 0))
        features.append(event.get('bytes_received', 0))
        features.append(event.get('requests_per_second', 0))
        features.append(event.get('unique_ports_accessed', 0))
        features.append(event.get('session_duration', 0))
        features.append(event.get('files_downloaded', 0))
        features.append(event.get('files_uploaded', 0))
        features.append(event.get('cpu_usage', 0))
        features.append(event.get('memory_usage', 0))
        
        # Time-based features
        timestamp = event.get('timestamp', datetime.utcnow().isoformat())
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            features.append(dt.hour)
            features.append(dt.weekday())
            features.append(1 if dt.weekday() >= 5 else 0)  # Weekend
        except:
            features.extend([0, 0, 0])
        
        # Boolean features (converted to 0/1)
        features.append(1 if event.get('is_encrypted', False) else 0)
        features.append(1 if event.get('is_root', False) else 0)
        features.append(1 if event.get('from_external', False) else 0)
        
        # IP-based features
        source_ip = event.get('source_ip', '0.0.0.0')
        if source_ip:
            try:
                octets = source_ip.split('.')
                if len(octets) == 4:
                    features.append(int(octets[0]))
                    features.append(int(octets[3]))
                    # Check if private IP
                    features.append(1 if octets[0] in ['10', '172', '192'] else 0)
                else:
                    features.extend([0, 0, 0])
            except:
                features.extend([0, 0, 0])
        else:
            features.extend([0, 0, 0])
        
        # Status code (if available)
        features.append(event.get('status_code', 0))
        
        # Request/response ratio
        requests = event.get('requests_count', 0)
        responses = event.get('responses_count', 0)
        features.append(requests / max(responses, 1))
        
        return np.array(features).reshape(1, -1)
    
    def train(self, events: List[Dict[str, Any]]):
        """Train the ML model on historical events"""
        logger.info(f"Training ML model on {len(events)} events...")
        
        if len(events) < 10:
            logger.warning("Not enough data to train (minimum 10 events required)")
            return False
        
        # Extract features from all events
        feature_matrix = []
        for event in events:
            features = self.extract_features(event)
            feature_matrix.append(features[0])
        
        X = np.array(feature_matrix)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Apply PCA if we have enough features
        if X_scaled.shape[1] > 10:
            X_scaled = self.pca.fit_transform(X_scaled)
        
        # Train model
        self.model.fit(X_scaled)
        self.is_trained = True
        self.training_data = X_scaled
        
        logger.info(f"✅ Model trained successfully on {len(events)} events")
        logger.info(f"   Feature dimensions: {X_scaled.shape[1]}")
        
        return True
    
    def detect_anomaly(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Detect if event is anomalous"""
        if not self.is_trained:
            return {
                'is_anomaly': False,
                'confidence': 0.0,
                'reason': 'Model not trained'
            }
        
        try:
            # Extract and scale features
            features = self.extract_features(event)
            features_scaled = self.scaler.transform(features)
            
            # Apply PCA if used during training
            if hasattr(self.pca, 'components_'):
                features_scaled = self.pca.transform(features_scaled)
            
            # Predict
            prediction = self.model.predict(features_scaled)[0]
            
            # Get anomaly score
            if hasattr(self.model, 'score_samples'):
                score = self.model.score_samples(features_scaled)[0]
                confidence = abs(score)
            else:
                score = self.model.decision_function(features_scaled)[0]
                confidence = abs(score)
            
            is_anomaly = (prediction == -1)
            
            result = {
                'is_anomaly': is_anomaly,
                'confidence': float(confidence),
                'score': float(score),
                'model_type': self.model_type,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            if is_anomaly:
                result['reason'] = self._explain_anomaly(event, features_scaled[0])
            
            return result
            
        except Exception as e:
            logger.error(f"Error detecting anomaly: {e}")
            return {
                'is_anomaly': False,
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _explain_anomaly(self, event: Dict[str, Any], features: np.ndarray) -> str:
        """Explain why event was flagged as anomaly"""
        reasons = []
        
        # Check for extreme values
        if event.get('failed_logins', 0) > 10:
            reasons.append(f"High failed login attempts ({event['failed_logins']})")
        
        if event.get('bytes_sent', 0) > 100000000:
            reasons.append(f"Large data transfer ({event['bytes_sent']} bytes)")
        
        if event.get('unique_ports_accessed', 0) > 20:
            reasons.append(f"Port scanning behavior ({event['unique_ports_accessed']} ports)")
        
        if event.get('requests_per_second', 0) > 100:
            reasons.append(f"High request rate ({event['requests_per_second']} req/s)")
        
        # Time-based
        try:
            timestamp = event.get('timestamp', datetime.utcnow().isoformat())
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            if dt.hour < 6 or dt.hour > 22:
                reasons.append(f"Unusual access time ({dt.hour}:00)")
        except:
            pass
        
        if not reasons:
            reasons.append("Statistical anomaly detected by ML model")
        
        return "; ".join(reasons)
    
    def save_model(self, filepath: str):
        """Save trained model to file"""
        if not self.is_trained:
            logger.warning("Cannot save untrained model")
            return False
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'pca': self.pca,
            'model_type': self.model_type,
            'contamination': self.contamination,
            'training_date': datetime.utcnow().isoformat()
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        logger.info(f"✅ Model saved to {filepath}")
        return True
    
    def load_model(self, filepath: str):
        """Load trained model from file"""
        try:
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.pca = model_data['pca']
            self.model_type = model_data['model_type']
            self.contamination = model_data['contamination']
            self.is_trained = True
            
            logger.info(f"✅ Model loaded from {filepath}")
            logger.info(f"   Trained on: {model_data.get('training_date', 'unknown')}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get model statistics"""
        return {
            'model_type': self.model_type,
            'is_trained': self.is_trained,
            'contamination': self.contamination,
            'training_samples': len(self.training_data) if self.training_data else 0
        }


def demo_ml_detector():
    """Demo the ML anomaly detector"""
    print("="*60)
    print("  ML ANOMALY DETECTOR DEMO")
    print("="*60)
    
    detector = MLAnomalyDetector(model_type='isolation_forest', contamination=0.1)
    
    # Generate training data (normal events)
    print("\n📊 Generating training data (normal events)...")
    training_events = []
    for i in range(100):
        event = {
            'failed_logins': np.random.randint(0, 3),
            'bytes_sent': np.random.randint(1000, 50000),
            'requests_per_second': np.random.randint(1, 10),
            'unique_ports_accessed': np.random.randint(1, 5),
            'timestamp': datetime.utcnow().isoformat(),
            'source_ip': f'10.0.{np.random.randint(1,255)}.{np.random.randint(1,255)}'
        }
        training_events.append(event)
    
    # Train model
    detector.train(training_events)
    
    # Test with normal event
    print("\n✅ Testing with normal event...")
    normal_event = {
        'failed_logins': 2,
        'bytes_sent': 25000,
        'requests_per_second': 5,
        'unique_ports_accessed': 3,
        'timestamp': datetime.utcnow().isoformat(),
        'source_ip': '10.0.1.50'
    }
    result = detector.detect_anomaly(normal_event)
    print(f"   Result: {'ANOMALY' if result['is_anomaly'] else 'NORMAL'}")
    print(f"   Confidence: {result['confidence']:.4f}")
    
    # Test with anomalous event
    print("\n⚠️  Testing with anomalous event...")
    anomalous_event = {
        'failed_logins': 50,  # Suspicious
        'bytes_sent': 500000000,  # Large transfer
        'requests_per_second': 1000,  # DDoS-like
        'unique_ports_accessed': 100,  # Port scan
        'timestamp': '2025-12-12T03:00:00Z',  # 3 AM
        'source_ip': '192.0.2.1'
    }
    result = detector.detect_anomaly(anomalous_event)
    print(f"   Result: {'ANOMALY' if result['is_anomaly'] else 'NORMAL'}")
    print(f"   Confidence: {result['confidence']:.4f}")
    if 'reason' in result:
        print(f"   Reason: {result['reason']}")
    
    # Save model
    print("\n💾 Saving model...")
    detector.save_model('models/ml_anomaly_detector.pkl')
    
    print("\n" + "="*60)
    print("  DEMO COMPLETE")
    print("="*60)


if __name__ == "__main__":
    import os
    os.makedirs('models', exist_ok=True)
    demo_ml_detector()
