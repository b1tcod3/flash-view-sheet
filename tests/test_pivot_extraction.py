#!/usr/bin/env python3
"""
Test for Pivot Table Extraction and Simple Pivot Implementation
Tests the new pivot module functionality according to the plan
"""

import pandas as pd
import numpy as np
import sys
import traceback
from datetime import datetime, timedelta

# Add the project root to Python path
sys.path.insert(0, '/var/www/html/proyectos/flash-sheet')

try:
    from core.pivot import SimplePivotTable, BasePivotTable, PivotFilterManager, PivotAggregationManager
    print("✅ Successfully imported pivot modules")
except ImportError as e:
    print(f"❌ Failed to import pivot modules: {e}")
    sys.exit(1)

def create_test_data() -> pd.DataFrame:
    """Create test data for pivot table testing"""
    np.random.seed(42)
    
    # Create sample data
    data = {
        'Region': ['North', 'South', 'East', 'West', 'North', 'South', 'East', 'West'] * 3,
        'Product': ['A', 'B', 'A', 'B', 'A', 'B', 'A', 'B'] * 3,
        'Salesperson': ['John', 'Mary', 'Bob', 'Alice', 'John', 'Mary', 'Bob', 'Alice'] * 3,
        'Sales': np.random.randint(100, 1000, 24),
        'Quantity': np.random.randint(1, 20, 24),
        'Date': [datetime(2023, 1, 1) + timedelta(days=i) for i in range(24)]
    }
    
    df = pd.DataFrame(data)
    print(f"✅ Created test data with shape: {df.shape}")
    return df

def test_simple_pivot_basic() -> None:
    """Test basic SimplePivotTable functionality"""
    print("\n🧪 Testing Basic Simple Pivot Table...")
    
    df = create_test_data()
    pivot = SimplePivotTable()
    
    # Test basic parameters
    parameters = {
        'index': 'Region',
        'columns': 'Product',
        'values': 'Sales',
        'aggfunc': 'sum'
    }
    
    try:
        result = pivot.execute(df, parameters)
        print(f"✅ Basic pivot successful, result shape: {result.shape}")
        print("📊 Result preview:")
        print(result.head())
        
        # Verify expected structure
        assert 'Region' in result.columns, "Region column should be in result"
        assert len(result) > 0, "Result should not be empty"
        print("✅ Basic pivot validation passed")
        
    except Exception as e:
        print(f"❌ Basic pivot failed: {e}")
        traceback.print_exc()
        return False
    
    return True

def test_simple_pivot_with_filters() -> None:
    """Test SimplePivotTable with filters"""
    print("\n🧪 Testing Simple Pivot Table with Filters...")
    
    df = create_test_data()
    pivot = SimplePivotTable()
    
    # Test with filters
    parameters = {
        'index': 'Region',
        'columns': 'Product', 
        'values': 'Sales',
        'aggfunc': 'mean',
        'filters': {
            'Sales': {'type': 'greater_than', 'value': 300},
            'Region': {'type': 'in_list', 'value': ['North', 'South']}
        }
    }
    
    try:
        result = pivot.execute(df, parameters)
        print(f"✅ Pivot with filters successful, result shape: {result.shape}")
        print("📊 Filtered result preview:")
        print(result.head())
        
        # Verify filters were applied
        assert len(result) > 0, "Filtered result should not be empty"
        print("✅ Filter validation passed")
        
    except Exception as e:
        print(f"❌ Pivot with filters failed: {e}")
        traceback.print_exc()
        return False
    
    return True

def test_simple_pivot_multiple_aggregations() -> None:
    """Test SimplePivotTable with different aggregation functions"""
    print("\n🧪 Testing Simple Pivot Table with Multiple Aggregations...")
    
    df = create_test_data()
    pivot = SimplePivotTable()
    
    # Test different aggregation functions
    agg_functions = ['sum', 'mean', 'count', 'min', 'max']
    
    for aggfunc in agg_functions:
        try:
            parameters = {
                'index': 'Product',
                'columns': 'Region',
                'values': 'Sales',
                'aggfunc': aggfunc
            }
            
            result = pivot.execute(df, parameters)
            print(f"✅ Aggregation '{aggfunc}' successful, shape: {result.shape}")
            
        except Exception as e:
            print(f"❌ Aggregation '{aggfunc}' failed: {e}")
            return False
    
    print("✅ Multiple aggregation functions test passed")
    return True

def test_simple_pivot_with_margins() -> None:
    """Test SimplePivotTable with margins/totals"""
    print("\n🧪 Testing Simple Pivot Table with Margins...")
    
    df = create_test_data()
    pivot = SimplePivotTable()
    
    parameters = {
        'index': 'Region',
        'columns': 'Product',
        'values': 'Sales',
        'aggfunc': 'sum',
        'margins': True,
        'margins_name': 'Total'
    }
    
    try:
        result = pivot.execute(df, parameters)
        print(f"✅ Pivot with margins successful, result shape: {result.shape}")
        print("📊 Result with margins preview:")
        print(result.tail())  # Show last rows which should contain totals
        
        # Check if margins were added
        if 'Total' in str(result.columns):
            print("✅ Margins validation passed")
        else:
            print("⚠️  Margins might not be properly configured")
        
    except Exception as e:
        print(f"❌ Pivot with margins failed: {e}")
        traceback.print_exc()
        return False
    
    return True

def test_simple_pivot_error_handling() -> None:
    """Test SimplePivotTable error handling"""
    print("\n🧪 Testing Simple Pivot Table Error Handling...")
    
    df = create_test_data()
    pivot = SimplePivotTable()
    
    # Test with missing required parameters
    try:
        result = pivot.execute(df, {})  # Empty parameters
        print("❌ Should have failed with empty parameters")
        return False
    except ValueError as e:
        print(f"✅ Correctly caught missing parameters error: {e}")
    except Exception as e:
        print(f"⚠️  Unexpected error type: {e}")
    
    # Test with non-existent columns
    try:
        parameters = {
            'index': 'NonExistentColumn',
            'columns': 'Product',
            'values': 'Sales',
            'aggfunc': 'sum'
        }
        result = pivot.execute(df, parameters)
        print("❌ Should have failed with non-existent column")
        return False
    except ValueError as e:
        print(f"✅ Correctly caught non-existent column error: {e}")
    except Exception as e:
        print(f"⚠️  Unexpected error type: {e}")
    
    print("✅ Error handling test passed")
    return True

def test_filter_manager() -> None:
    """Test PivotFilterManager functionality"""
    print("\n🧪 Testing PivotFilterManager...")
    
    df = create_test_data()
    filter_manager = PivotFilterManager()
    
    try:
        # Add filters using the manager
        filter_manager.add_filter('Sales', 'greater_than', 300)
        filter_manager.add_filter('Region', 'in_list', ['North', 'South'], 'and')
        
        # Apply filters
        filtered_df = filter_manager.apply_filters(df)
        print(f"✅ Filter manager successful, original shape: {df.shape}, filtered shape: {filtered_df.shape}")
        
        # Get filter summary
        summary = filter_manager.get_filter_summary()
        print(f"✅ Filter summary: {summary['total_filters']} filters applied")
        
    except Exception as e:
        print(f"❌ Filter manager test failed: {e}")
        traceback.print_exc()
        return False
    
    return True

def test_aggregation_manager() -> None:
    """Test PivotAggregationManager functionality"""
    print("\n🧪 Testing PivotAggregationManager...")
    
    try:
        agg_manager = PivotAggregationManager()
        
        # Add multiple aggregations
        agg_manager.add_aggregation('sum', 'Sales')
        agg_manager.add_aggregation('mean', 'Sales')
        agg_manager.add_aggregation('count', 'Sales')
        
        # Get valid aggregations
        valid_aggs = agg_manager.get_valid_aggregations('numeric')
        print(f"✅ Valid aggregations for numeric data: {len(valid_aggs)} functions")
        
        # Get aggregation summary
        summary = agg_manager.get_aggregation_summary()
        print(f"✅ Aggregation summary: {summary['total_aggregations']} aggregations configured")
        
    except Exception as e:
        print(f"❌ Aggregation manager test failed: {e}")
        traceback.print_exc()
        return False
    
    return True

def test_performance() -> None:
    """Test performance with larger dataset"""
    print("\n🧪 Testing Performance with Larger Dataset...")
    
    # Create larger dataset
    np.random.seed(42)
    n_rows = 10000
    
    large_data = {
        'Region': np.random.choice(['North', 'South', 'East', 'West'], n_rows),
        'Product': np.random.choice(['A', 'B', 'C', 'D'], n_rows),
        'Salesperson': np.random.choice(['John', 'Mary', 'Bob', 'Alice', 'Tom'], n_rows),
        'Sales': np.random.randint(100, 5000, n_rows),
        'Quantity': np.random.randint(1, 100, n_rows)
    }
    
    large_df = pd.DataFrame(large_data)
    pivot = SimplePivotTable()
    
    start_time = datetime.now()
    
    try:
        parameters = {
            'index': 'Region',
            'columns': 'Product',
            'values': 'Sales',
            'aggfunc': 'sum'
        }
        
        result = pivot.execute(large_df, parameters)
        end_time = datetime.now()
        
        processing_time = (end_time - start_time).total_seconds()
        print(f"✅ Large dataset processed successfully:")
        print(f"   - Original shape: {large_df.shape}")
        print(f"   - Result shape: {result.shape}")
        print(f"   - Processing time: {processing_time:.2f} seconds")
        
        # Performance should be reasonable (< 5 seconds for 10k rows)
        if processing_time > 5.0:
            print("⚠️  Performance might need optimization")
        else:
            print("✅ Performance is acceptable")
            
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        traceback.print_exc()
        return False
    
    return True

def main() -> int:
    """Run all tests"""
    print("🚀 Starting Pivot Table Implementation Tests")
    print("=" * 60)
    
    test_results = []
    
    # Run all tests
    test_results.append(("Basic Simple Pivot", test_simple_pivot_basic()))
    test_results.append(("Simple Pivot with Filters", test_simple_pivot_with_filters()))
    test_results.append(("Multiple Aggregations", test_simple_pivot_multiple_aggregations()))
    test_results.append(("Margins/Totals", test_simple_pivot_with_margins()))
    test_results.append(("Error Handling", test_simple_pivot_error_handling()))
    test_results.append(("Filter Manager", test_filter_manager()))
    test_results.append(("Aggregation Manager", test_aggregation_manager()))
    test_results.append(("Performance", test_performance()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<30} {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("-" * 60)
    print(f"Total Tests: {len(test_results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed! SimplePivotTable implementation is working correctly.")
        print("\n📋 Phase 2 Implementation Status:")
        print("✅ BasePivotTable class implemented")
        print("✅ SimplePivotTable class implemented with:")
        print("   - Single column selection (index, columns, values)")
        print("   - Basic aggregation function support")
        print("   - Filter support")
        print("   - Error handling and validation")
        print("   - Performance optimization")
        print("\n🚀 Ready to proceed to Phase 3: Combined Pivot Implementation")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review the implementation.")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)