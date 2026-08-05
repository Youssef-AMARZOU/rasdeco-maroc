"""
Data Cleaning & Feature Engineering Utility Script
===================================================
Reusable functions for data preprocessing, cleaning, and feature engineering.
Set this as a Utility Script on Kaggle to import into other notebooks.

Usage:
    from dataprep import clean_missing, encode_categoricals, engineer_features
"""

import pandas as pd
import numpy as np
from typing import Optional, List, Tuple


def load_dataset(path: str) -> pd.DataFrame:
    """Load dataset from CSV or Parquet."""
    if path.endswith('.parquet'):
        return pd.read_parquet(path)
    return pd.read_csv(path)


def info_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Get comprehensive dataset info in one DataFrame."""
    summary = pd.DataFrame({
        'dtype': df.dtypes,
        'non_null': df.notna().sum(),
        'null_count': df.isna().sum(),
        'null_pct': (df.isna().sum() / len(df) * 100).round(2),
        'n_unique': df.nunique(),
        'sample': [df[col].dropna().iloc[0] if df[col].dropna().shape[0] > 0 else None for col in df.columns]
    })
    return summary


def clean_missing(df: pd.DataFrame, strategy: str = 'auto') -> pd.DataFrame:
    """
    Clean missing values.
    
    Strategies:
    - 'auto': numeric -> median, categorical -> mode
    - 'drop': drop rows with any null
    - 'fill': fill numeric with 0, categorical with 'Unknown'
    """
    df = df.copy()
    
    if strategy == 'drop':
        return df.dropna()
    
    for col in df.columns:
        if df[col].isna().sum() == 0:
            continue
            
        if strategy == 'auto':
            if df[col].dtype in ['int64', 'float64']:
                df[col] = df[col].fillna(df[col].median())
            else:
                mode_val = df[col].mode()
                df[col] = df[col].fillna(mode_val.iloc[0] if len(mode_val) > 0 else 'Unknown')
        elif strategy == 'fill':
            if df[col].dtype in ['int64', 'float64']:
                df[col] = df[col].fillna(0)
            else:
                df[col] = df[col].fillna('Unknown')
    
    return df


def detect_outliers(df: pd.DataFrame, col: str, method: str = 'iqr', threshold: float = 1.5) -> pd.Series:
    """Detect outliers using IQR or Z-score method."""
    if method == 'iqr':
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - threshold * iqr
        upper = q3 + threshold * iqr
        return (df[col] < lower) | (df[col] > upper)
    elif method == 'zscore':
        from scipy import stats
        z = np.abs(stats.zscore(df[col].dropna()))
        mask = pd.Series(False, index=df.index)
        mask[df[col].dropna().index] = z > threshold
        return mask


def cap_outliers(df: pd.DataFrame, col: str, method: str = 'iqr', threshold: float = 1.5) -> pd.DataFrame:
    """Cap outliers to IQR bounds."""
    df = df.copy()
    if method == 'iqr':
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - threshold * iqr
        upper = q3 + threshold * iqr
        df[col] = df[col].clip(lower, upper)
    return df


def encode_categoricals(df: pd.DataFrame, columns: Optional[List[str]] = None, method: str = 'onehot') -> pd.DataFrame:
    """
    Encode categorical variables.
    
    Methods:
    - 'onehot': One-hot encoding
    - 'label': Label encoding
    - 'target': Target encoding (requires y)
    """
    df = df.copy()
    if columns is None:
        columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    if method == 'onehot':
        return pd.get_dummies(df, columns=columns, drop_first=True)
    elif method == 'label':
        from sklearn.preprocessing import LabelEncoder
        le = LabelEncoder()
        for col in columns:
            df[col] = le.fit_transform(df[col].astype(str))
        return df
    
    return df


def scale_numeric(df: pd.DataFrame, columns: Optional[List[str]] = None, method: str = 'standard') -> pd.DataFrame:
    """
    Scale numeric features.
    
    Methods:
    - 'standard': StandardScaler (mean=0, std=1)
    - 'minmax': MinMaxScaler (0-1)
    - 'robust': RobustScaler (median-based)
    """
    from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
    
    df = df.copy()
    if columns is None:
        columns = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    
    scalers = {
        'standard': StandardScaler,
        'minmax': MinMaxScaler,
        'robust': RobustScaler
    }
    
    scaler = scalers[method]()
    df[columns] = scaler.fit_transform(df[columns])
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Apply common feature engineering transformations."""
    df = df.copy()
    
    for col in df.select_dtypes(include=['int64', 'float64']).columns:
        # Log transform for skewed numeric columns
        if df[col].skew() > 1:
            df[f'{col}_log'] = np.log1p(df[col].clip(lower=0))
        
        # Binning for high-cardinality numerics
        if df[col].nunique() > 20:
            df[f'{col}_bin'] = pd.qcut(df[col], q=5, labels=False, duplicates='drop')
    
    return df


def correlation_analysis(df: pd.DataFrame, threshold: float = 0.8) -> pd.DataFrame:
    """Find highly correlated feature pairs."""
    corr = df.select_dtypes(include=['int64', 'float64']).corr()
    pairs = []
    for i in range(len(corr.columns)):
        for j in range(i+1, len(corr.columns)):
            if abs(corr.iloc[i, j]) > threshold:
                pairs.append({
                    'feature_1': corr.columns[i],
                    'feature_2': corr.columns[j],
                    'correlation': round(corr.iloc[i, j], 3)
                })
    return pd.DataFrame(pairs).sort_values('correlation', ascending=False)


def prepare_for_modeling(df: pd.DataFrame, target: str) -> Tuple[pd.DataFrame, pd.Series]:
    """Full preprocessing pipeline: clean + encode + scale."""
    df = df.copy()
    y = df[target]
    X = df.drop(columns=[target])
    
    X = clean_missing(X, strategy='auto')
    X = encode_categoricals(X, method='onehot')
    X = scale_numeric(X, method='standard')
    
    return X, y
