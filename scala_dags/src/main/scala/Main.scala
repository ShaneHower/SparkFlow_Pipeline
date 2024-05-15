import com.main.AthenaConnection

object Main {

    def main(args: Array[String]): Unit = {
        // Load AWS credentials from ~/.aws/credentials
        val db: AthenaConnection = new AthenaConnection()
        val sql: String = "select * from finances.capital_one_temp limit 100"
        db.Select(sql)
    }
}
