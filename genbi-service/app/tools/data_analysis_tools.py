"""
Data analysis tools for genbi-core.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import json
from .base_tool import BaseTool, ToolType, ToolParameter


class DataAnalysisTool(BaseTool):
    """Tool for basic data analysis operations."""
    
    def __init__(self):
        super().__init__(
            name="data_analysis",
            description="Perform basic data analysis on datasets",
            tool_type=ToolType.DATA_ANALYSIS
        )
    
    def _setup_parameters(self) -> None:
        self.parameters = [
            ToolParameter(
                name="data",
                type="string",
                description="Data to analyze (JSON string, CSV string, or file path)",
                required=True
            ),
            ToolParameter(
                name="analysis_type",
                type="string",
                description="Type of analysis to perform",
                required=True,
                enum=["summary", "correlation", "distribution", "outliers", "trends"]
            ),
            ToolParameter(
                name="data_format",
                type="string",
                description="Format of the input data",
                required=False,
                default="json",
                enum=["json", "csv", "file_path"]
            ),
            ToolParameter(
                name="columns",
                type="array",
                description="Specific columns to analyze (optional)",
                required=False
            )
        ]
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        try:
            self.validate_parameters(**kwargs)
            
            data = kwargs["data"]
            analysis_type = kwargs["analysis_type"]
            data_format = kwargs.get("data_format", "json")
            columns = kwargs.get("columns")
            
            # Load data
            df = await self._load_data(data, data_format)
            
            # Select columns if specified
            if columns:
                df = df[columns]
            
            # Perform analysis
            result = await self._perform_analysis(df, analysis_type)
            
            return {
                "result": result,
                "success": True,
                "error": None
            }
            
        except Exception as e:
            return {
                "result": None,
                "success": False,
                "error": str(e)
            }
    
    async def _load_data(self, data: str, data_format: str) -> pd.DataFrame:
        """Load data into pandas DataFrame."""
        if data_format == "json":
            return pd.read_json(data)
        elif data_format == "csv":
            return pd.read_csv(data)
        elif data_format == "file_path":
            if data.endswith('.csv'):
                return pd.read_csv(data)
            elif data.endswith('.json'):
                return pd.read_json(data)
            else:
                raise ValueError(f"Unsupported file format: {data}")
        else:
            raise ValueError(f"Unsupported data format: {data_format}")
    
    async def _perform_analysis(self, df: pd.DataFrame, analysis_type: str) -> Dict[str, Any]:
        """Perform the specified analysis."""
        if analysis_type == "summary":
            return self._summary_analysis(df)
        elif analysis_type == "correlation":
            return self._correlation_analysis(df)
        elif analysis_type == "distribution":
            return self._distribution_analysis(df)
        elif analysis_type == "outliers":
            return self._outlier_analysis(df)
        elif analysis_type == "trends":
            return self._trend_analysis(df)
        else:
            raise ValueError(f"Unsupported analysis type: {analysis_type}")
    
    def _summary_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform summary statistics analysis."""
        return {
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "data_types": df.dtypes.to_dict(),
            "missing_values": df.isnull().sum().to_dict(),
            "summary_stats": df.describe().to_dict(),
            "memory_usage": df.memory_usage(deep=True).sum()
        }
    
    def _correlation_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform correlation analysis."""
        numeric_df = df.select_dtypes(include=[np.number])
        if numeric_df.empty:
            return {"error": "No numeric columns found for correlation analysis"}
        
        correlation_matrix = numeric_df.corr()
        return {
            "correlation_matrix": correlation_matrix.to_dict(),
            "high_correlations": self._find_high_correlations(correlation_matrix)
        }
    
    def _distribution_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform distribution analysis."""
        distributions = {}
        for column in df.columns:
            if df[column].dtype in ['int64', 'float64']:
                distributions[column] = {
                    "mean": df[column].mean(),
                    "median": df[column].median(),
                    "std": df[column].std(),
                    "skewness": df[column].skew(),
                    "kurtosis": df[column].kurtosis()
                }
            else:
                distributions[column] = {
                    "unique_values": df[column].nunique(),
                    "most_common": df[column].value_counts().head(5).to_dict()
                }
        
        return {"distributions": distributions}
    
    def _outlier_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform outlier analysis."""
        outliers = {}
        for column in df.select_dtypes(include=[np.number]).columns:
            Q1 = df[column].quantile(0.25)
            Q3 = df[column].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outlier_indices = df[(df[column] < lower_bound) | (df[column] > upper_bound)].index.tolist()
            outliers[column] = {
                "outlier_count": len(outlier_indices),
                "outlier_percentage": len(outlier_indices) / len(df) * 100,
                "outlier_indices": outlier_indices[:10]  # Limit to first 10
            }
        
        return {"outliers": outliers}
    
    def _trend_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform trend analysis."""
        trends = {}
        for column in df.select_dtypes(include=[np.number]).columns:
            if len(df) > 1:
                # Simple linear trend
                x = np.arange(len(df))
                y = df[column].values
                slope = np.polyfit(x, y, 1)[0]
                
                trends[column] = {
                    "trend_direction": "increasing" if slope > 0 else "decreasing",
                    "trend_strength": abs(slope),
                    "slope": slope
                }
        
        return {"trends": trends}
    
    def _find_high_correlations(self, correlation_matrix: pd.DataFrame, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Find high correlations above threshold."""
        high_correlations = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                corr_value = correlation_matrix.iloc[i, j]
                if abs(corr_value) >= threshold:
                    high_correlations.append({
                        "column1": correlation_matrix.columns[i],
                        "column2": correlation_matrix.columns[j],
                        "correlation": corr_value
                    })
        
        return sorted(high_correlations, key=lambda x: abs(x["correlation"]), reverse=True)


class StatisticalAnalysisTool(BaseTool):
    """Tool for advanced statistical analysis."""
    
    def __init__(self):
        super().__init__(
            name="statistical_analysis",
            description="Perform advanced statistical analysis including hypothesis testing",
            tool_type=ToolType.DATA_ANALYSIS
        )
    
    def _setup_parameters(self) -> None:
        self.parameters = [
            ToolParameter(
                name="data",
                type="string",
                description="Data to analyze (JSON string or file path)",
                required=True
            ),
            ToolParameter(
                name="test_type",
                type="string",
                description="Type of statistical test to perform",
                required=True,
                enum=["t_test", "anova", "chi_square", "correlation_test", "normality_test"]
            ),
            ToolParameter(
                name="group_column",
                type="string",
                description="Column to use for grouping (for t-test, ANOVA)",
                required=False
            ),
            ToolParameter(
                name="value_column",
                type="string",
                description="Column containing values to test",
                required=False
            ),
            ToolParameter(
                name="alpha",
                type="float",
                description="Significance level (default: 0.05)",
                required=False,
                default=0.05
            )
        ]
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        try:
            self.validate_parameters(**kwargs)
            
            data = kwargs["data"]
            test_type = kwargs["test_type"]
            group_column = kwargs.get("group_column")
            value_column = kwargs.get("value_column")
            alpha = kwargs.get("alpha", 0.05)
            
            # Load data
            df = await self._load_data(data)
            
            # Perform statistical test
            result = await self._perform_statistical_test(
                df, test_type, group_column, value_column, alpha
            )
            
            return {
                "result": result,
                "success": True,
                "error": None
            }
            
        except Exception as e:
            return {
                "result": None,
                "success": False,
                "error": str(e)
            }
    
    async def _load_data(self, data: str) -> pd.DataFrame:
        """Load data into pandas DataFrame."""
        try:
            return pd.read_json(data)
        except:
            return pd.read_csv(data)
    
    async def _perform_statistical_test(
        self, 
        df: pd.DataFrame, 
        test_type: str, 
        group_column: Optional[str], 
        value_column: Optional[str], 
        alpha: float
    ) -> Dict[str, Any]:
        """Perform the specified statistical test."""
        from scipy import stats
        
        if test_type == "t_test":
            return self._t_test(df, group_column, value_column, alpha)
        elif test_type == "anova":
            return self._anova_test(df, group_column, value_column, alpha)
        elif test_type == "chi_square":
            return self._chi_square_test(df, group_column, value_column, alpha)
        elif test_type == "correlation_test":
            return self._correlation_test(df, alpha)
        elif test_type == "normality_test":
            return self._normality_test(df, value_column, alpha)
        else:
            raise ValueError(f"Unsupported test type: {test_type}")
    
    def _t_test(self, df: pd.DataFrame, group_column: str, value_column: str, alpha: float) -> Dict[str, Any]:
        """Perform t-test."""
        groups = df[group_column].unique()
        if len(groups) != 2:
            raise ValueError("T-test requires exactly 2 groups")
        
        group1_data = df[df[group_column] == groups[0]][value_column]
        group2_data = df[df[group_column] == groups[1]][value_column]
        
        t_stat, p_value = stats.ttest_ind(group1_data, group2_data)
        
        return {
            "test_type": "t_test",
            "t_statistic": t_stat,
            "p_value": p_value,
            "significant": p_value < alpha,
            "group1": groups[0],
            "group2": groups[1],
            "group1_mean": group1_data.mean(),
            "group2_mean": group2_data.mean()
        }
    
    def _anova_test(self, df: pd.DataFrame, group_column: str, value_column: str, alpha: float) -> Dict[str, Any]:
        """Perform ANOVA test."""
        groups = df[group_column].unique()
        if len(groups) < 2:
            raise ValueError("ANOVA requires at least 2 groups")
        
        group_data = [df[df[group_column] == group][value_column] for group in groups]
        f_stat, p_value = stats.f_oneway(*group_data)
        
        return {
            "test_type": "anova",
            "f_statistic": f_stat,
            "p_value": p_value,
            "significant": p_value < alpha,
            "groups": groups.tolist(),
            "group_means": {group: df[df[group_column] == group][value_column].mean() for group in groups}
        }
    
    def _chi_square_test(self, df: pd.DataFrame, group_column: str, value_column: str, alpha: float) -> Dict[str, Any]:
        """Perform chi-square test."""
        contingency_table = pd.crosstab(df[group_column], df[value_column])
        chi2_stat, p_value, dof, expected = stats.chi2_contingency(contingency_table)
        
        return {
            "test_type": "chi_square",
            "chi2_statistic": chi2_stat,
            "p_value": p_value,
            "degrees_of_freedom": dof,
            "significant": p_value < alpha,
            "contingency_table": contingency_table.to_dict()
        }
    
    def _correlation_test(self, df: pd.DataFrame, alpha: float) -> Dict[str, Any]:
        """Perform correlation test."""
        numeric_df = df.select_dtypes(include=[np.number])
        if numeric_df.shape[1] < 2:
            raise ValueError("Correlation test requires at least 2 numeric columns")
        
        correlations = {}
        for i, col1 in enumerate(numeric_df.columns):
            for col2 in numeric_df.columns[i+1:]:
                corr, p_value = stats.pearsonr(numeric_df[col1], numeric_df[col2])
                correlations[f"{col1}_vs_{col2}"] = {
                    "correlation": corr,
                    "p_value": p_value,
                    "significant": p_value < alpha
                }
        
        return {
            "test_type": "correlation_test",
            "correlations": correlations
        }
    
    def _normality_test(self, df: pd.DataFrame, value_column: str, alpha: float) -> Dict[str, Any]:
        """Perform normality test (Shapiro-Wilk)."""
        data = df[value_column].dropna()
        if len(data) < 3:
            raise ValueError("Normality test requires at least 3 data points")
        
        statistic, p_value = stats.shapiro(data)
        
        return {
            "test_type": "normality_test",
            "statistic": statistic,
            "p_value": p_value,
            "is_normal": p_value > alpha,
            "sample_size": len(data)
        } 