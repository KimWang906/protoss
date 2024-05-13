#include <iostream>
#include <mysql/mysql.h>
#include <signal.h>
#include <fcntl.h>
#include <string>
#include <fmt/core.h>

using namespace std;

class MySQLClient
{
public:
    MYSQL *conn;
    const char *hostname;
    const char *username;
    const char *password;
    const char *db_name;
    MySQLClient()
    {
        this->hostname = "poc_no_lib_db";
        this->username = "poc";
        this->password = "poc";
        this->db_name = "poc_db";
        this->conn = nullptr;
    }

    void init_mysql_connect()
    {
        this->conn = mysql_init(nullptr);

        if (!mysql_real_connect(
                this->conn,
                this->hostname,
                this->username,
                this->password,
                this->db_name,
                0,
                nullptr,
                0))
        {
            cout << "[MySQL] Connection Error" << endl;
            exit(-1);
        }
    }

    void handle_error(int status_code)
    {
        if (status_code == 0x426)
            cout << "Duplicate ID" << endl;
    }

    void exec_query(string SQLquery)
    {
        int status_code;
        if (SQLquery.empty())
            exit(-1);
        mysql_query(this->conn, SQLquery.c_str());
        status_code = mysql_errno(this->conn);
        handle_error(status_code);
    }

    MYSQL_RES *exec_query_result(string SQLquery)
    {
        if (SQLquery.empty())
            exit(-1);
        mysql_query(this->conn, SQLquery.c_str());

        return mysql_store_result(this->conn);
    }
};

MySQLClient *client;

void handler()
{
    void *buf = (void *)new char[0x2800];
    int fd = open("/proc/self/maps", O_RDONLY);
    read(fd, buf, 0x2800);
    write(1, buf, 0x2800);
    exit(-1);
}

sighandler_t init()
{
    void *buf = (void *)new char[0x400];
    setvbuf(stdin, 0, 2, 0);
    setvbuf(stdout, 0, 2, 0);
    system("mysql -hpoc_no_lib_db -upoc -ppoc < /home/user/init.sql");
    MySQLClient *mysql_handler = new MySQLClient();
    client = mysql_handler;
    mysql_handler->init_mysql_connect();
    int fd = open("flag_1", O_RDONLY);
    read(fd, buf, 0x400);
    return signal(SIGSEGV, (sighandler_t)handler);
}

int main()
{
    init();
    /*
        dummy -> dummy -> victim -> data...
    */
    void ****victim = new void ***;
    *victim = new void **;                             // dereference once
    **victim = new void *;                             // dereference twice
    ***victim = (void *)string("HELLO WORLD!").data(); // dereference thrice

    cout << "Victim: " << **victim << endl;

    client->exec_query("UPDATE ")

    return 0;
}