package com.main

import java.sql.{Connection, DriverManager, ResultSet}
import software.amazon.awssdk.auth.credentials.{ProfileCredentialsProvider, AwsCredentials}

class AthenaConnection {

    def SetUpConnection(): Connection = {
        val credentials: AwsCredentials = ProfileCredentialsProvider.create().resolveCredentials()
        val athenaUrl: String = "jdbc:awsathena://AwsRegion=us-east-1"
        val s3_bucket: String = "s3://picklepokeyhouse/athena_query_output/"

        // JDBC connection properties
        val properties = new java.util.Properties()
        properties.setProperty("user", credentials.accessKeyId())
        properties.setProperty("password", credentials.secretAccessKey())
        properties.setProperty("S3OutputLocation", s3_bucket)  // Adjust the S3 bucket accordingly

        // Load the JDBC driver
        Class.forName("com.simba.athena.jdbc.Driver")

        // Establish a connection to Athena
        val connection: Connection = DriverManager.getConnection(athenaUrl, properties)
        connection
    }

    def Select(query: String): Unit = {
        val connection: Connection = SetUpConnection()

        // Execute the query
        val statement = connection.createStatement()
        val resultSet: ResultSet = statement.executeQuery(query)

        // Print the results
        while (resultSet.next()) {
            println(resultSet.getString(1) + ", " + resultSet.getString(2))
        }

        // Close the resources
        resultSet.close()
        statement.close()
        connection.close()
    }
}
