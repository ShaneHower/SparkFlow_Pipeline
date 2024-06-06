package com.main

import org.apache.spark.sql.{DataFrame, SparkSession}
import software.amazon.awssdk.auth.credentials.{ProfileCredentialsProvider, AwsCredentials}
import org.apache.hadoop.fs.s3a.S3AFileSystem


// object Config {
//     val credentials: AwsCredentials = ProfileCredentialsProvider.create().resolveCredentials()
//     val accessKeyId: String = credentials.accessKeyId()
//     val secretAccessKey: String = credentials.secretAccessKey()
// }


object DAGManager {

    def main(args: Array[String]): Unit = {
        println("starting connection")
        val spark = SparkSession.builder()
            .appName("Read S3 Test")
            // NOTE: These are used when locally developing we may want to add functionality of "local" vs "cloud" development
            // .config("spark.hadoop.fs.s3a.access.key", Config.accessKeyId)
            // .config("spark.hadoop.fs.s3a.secret.key", Config.secretAccessKey)
            .config("spark.hadoop.fs.s3a.impl", classOf[S3AFileSystem].getName)
            .config("spark.hadoop.fs.s3a.endpoint", "s3.amazonaws.com")
            .config("spark.hadoop.fs.s3a.path.style.access", "true")
            .getOrCreate()
        println("connection made")

        val s3Path: String = "s3a://picklepokeyhouse/finances/monitored_input/capital_one/input/qucksilver_202401_to_202404.csv"

        println("reading file")
        val df: DataFrame = spark.read.text(s3Path)

        df.show()

        spark.stop()
    }
}
