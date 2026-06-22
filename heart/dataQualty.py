def data_quality_percentage(data_values):

                # Calculate the number of valid entries (not None or 'None')
    valid_count = sum(1 for value in data_values.values() if value is not None and value != 'None')
    total_columns = len(data_values)
     

    # Calculate the percentage of valid data
    data_quality_value = (valid_count / total_columns) * 100 if total_columns > 0 else 0
    return data_quality_value


test_data = {
    'age': 24,
    'sex': '0',
    'chestpain': '1',
    'restingBP': None,
    'cholesterol': None,
    'fastingbloodsugar': '0',
    'restingrelectro': '1',
    'maxheartrate': 133,
    'exerciseangia': '0',
    'oldpeak': None,
    'slope': '1',
    'noofmajorvessels': '0'
}

print(f'test data percentage {data_quality_percentage(test_data)}')  # Should show a percentage less than 100
