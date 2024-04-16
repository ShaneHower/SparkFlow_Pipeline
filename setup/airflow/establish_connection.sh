#!/bin/bash

# Check if Spark connection already exists
if airflow connections get spark_default; then
    echo "Spark connection already exists"
else
    # Attempt to add Spark connection
    if airflow connections add spark_default --conn-type spark --conn-host spark://spark-master:7077; then
        echo "Spark connection added successfully"
    else
        echo "Failed to add Spark connection"
    fi
fi
