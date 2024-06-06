name := "DAG Manager"

version := "1.0"

scalaVersion := "2.12.18"

libraryDependencies ++= Seq(
  "org.apache.spark" %% "spark-sql" % "3.5.1",
  "org.apache.hadoop" % "hadoop-aws" % "3.3.1",
  "org.apache.hadoop" % "hadoop-common" % "3.3.1",
  "software.amazon.awssdk" % "auth" % "2.20.28", // AWS SDK Auth module
  "software.amazon.awssdk" % "core" % "2.20.28" // AWS SDK Core module
)
