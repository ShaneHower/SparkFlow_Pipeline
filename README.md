# SparkFlow


### Overview
This project was used to learn more about Data Engineering.  Specifically I wanted to get some experience using Docker, Spark, Airflow, and Terraform.  The infrastructure for this project can be used for any kind of data, however, I will be validating and processing my household finances.  Again the main motivation for this repository is to learn and get experience with new tools, that being said, if I'm going to analyze data, I would like to analyze something that will be beneficial to me.  Given that the use case of the data is very personal, I won't be publishing any real data/insights within this project.  Any examples that I use to showcase the functionality of the system I built will be built from randomly generated data based off of the structure of my database.

One important note before moving on, since this is a personal project that utilizes AWS, I will be minimizing up time and costs as much as possible.  Obviously I do not want to spend a ton of money on a personal experiment, and my tech stack will be running so infrequently that it wouldn't make sense to keep resources running.  This means that approaches that I take may not be the most conventional use of a given tool.  For example, I utilize airflow in this project.  In a professional productionized environment, you would probably want to keep the airflow instance up 100% of the time.  For me, I will have a handful of DAGs that will run infrequently, it does not make sense to pay for the EC2 to run indefinitely.  I also wanted to really focus on [IaC](https://en.wikipedia.org/wiki/Infrastructure_as_code) in this project, building up and tearing down services as needed not only made sense for costs, but met this goal.

### How it Works
![alt text](png/infrastructure.png)

There are multiple components to this infrastructure, they will all revolve around a data lake that will be stored on S3. I will be processing raw data files that get dropped in S3 and query them using the serverless database Athena.  This worked well for my use case as my database is small.  Athena is lightweight and requires almost no setup, vs something more robust like redshift that would require more work up front to get up and running.  Here is how the process works:

1. A lambda function monitors a specific location in my S3 bucket.  When a raw file is dropped in the monitored path, it spins up an EC2.  It feeds in some intial set up instructions to the EC2 on launch, namely installing dependencies like git and docker, pulling down my repository, and launching the sparkflow container using my [docker-compose](/sparkflow/docker-compose.yml).
2. Once the EC2 is launched and the SparkFlow container is up and running, the DAG that corresponds with the input file will be triggered.  The Airflow DAGs do not contain the bulk of the ETL logic.  I wanted to learn more spark within this project, and therefore all of my DAGs are technically written in scala.  These scala files will get compiled into their respective JAR files during the CICD step, Airflow will pass these JAR files to the Spark cluster where they will be executed.  Airflow will wait for the cluster to finish running the JAR file and return back the pass/failure of the pipeline.  The Scala Spark process will write the processed files directly to S3, where Athena can then query them.
3. The final piece of this project is putting together some kind of dashboard to visualize and analyze the data.  I will most likely be using apache superset as it is a free and open sourced dashboarding tool.  This would require another EC2 to host the superset environment.  So far, this is the piece that I have thought about the least and may change as I work through the rest of the infrastructure.

### Development
The Launch.json has configurations that allow you to quickly run [launch_develop_env.py](/infra/cloud_develop/launch_develop_env.py).  This py file will launch and initialize an EC2 with a "production-like" environment.  It triggers the lambda which spins up the ec2 and sets up the repository and docker containers.  Once the EC2 is running, the code will create the SSH connection from your local computer to the newly spun up EC2.  This allows us to develop in the cloud within an environment that is as close to production as possible.  This means we can limit the amount of requirements/configurations locally and we can get to work developing within this repo a lot faster.  There are only two prerequisites which will allow you to use this script
1. Download [Remote-SSH](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-ssh) from VS Code
2. Set up your aws credentials locally (see instructions [here](https://docs.aws.amazon.com/sdk-for-java/v1/developer-guide/setup-credentials.html))
3. The pem file must be in the top level of your local environment.  For obvious reasons the pem file is not stored in this repository.  You can get it from AWS.  If you need to convert a ppk file to pem, use PUTTYgen (PUTTYgen comes with [Putty](https://www.putty.org/))
Once [launch_develop_env.py](/infra/cloud_develop/launch_develop_env.py) runs you will see the IP of the EC2 within the Remote Explorer on VSCode.  At this point you can connect and start developing/testing new features within this repository.
