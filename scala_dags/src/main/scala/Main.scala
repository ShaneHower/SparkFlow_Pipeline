package com.main

import org.apache.spark.sql.{DataFrame, SparkSession}
import org.apache.hadoop.fs.{FileSystem, Path}
import org.apache.hadoop.fs.s3a.S3AFileSystem
import scala.collection.mutable.ListBuffer


object DAGManager {

    def main(args: Array[String]): Unit = {
        println("starting connection")
        val spark = SparkSession.builder()
            .appName("Read S3 Test")
            .config("spark.hadoop.fs.s3a.impl", classOf[S3AFileSystem].getName)
            .config("spark.hadoop.fs.s3a.endpoint", "s3.amazonaws.com")
            .config("spark.hadoop.fs.s3a.path.style.access", "true")
            .getOrCreate()
        println("connection made")

        val s3Path: String = "s3a://picklepokeyhouse/finances/monitored_input/input/capital_one/"

        // List all files in the given S3 path
        val fs = FileSystem.get(spark.sparkContext.hadoopConfiguration)
        val path = new Path(s3Path)
        val fileStatuses = fs.listStatus(path)
        val filesList = ListBuffer[String]()

        

        for (status <- fileStatuses) {
            if (status.isFile) {
                filesList += status.getPath.toString
            }
        }

        println("Files found:")
        filesList.foreach(println)

        // Read all files into a DataFrame
        println("reading files")
        val df: DataFrame = spark.read.text(filesList: _*)

        df.show()

        spark.stop()
    }
}
