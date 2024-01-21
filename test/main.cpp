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
        this->hostname = "poc_db";
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
    system("mysql -hpoc_db -upoc -ppoc < /home/user/init.sql");
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
    int input;
    while (1)
    {
        cout << "Select Options" << endl;
        cout << "1. Write memo" << endl;
        cout << "2. Search memo" << endl;
        cout << "3. Exit" << endl;
        cout << "Input: ";
        cin >> input;
        cin.ignore();

        if (input == 1)
        {
            MySQLClient *conn = client;
            string title, memo;
            // string format = "INSERT INTO memo(title, msg) VALUES(\"%s\", \"%s\");";
            cout << "Write memo" << endl;
            cout << "title: ";
            getline(cin, title);
            cout << "memo: ";
            getline(cin, memo);

            // char *buffer = new char[format.size() +
            //                         title.size() +
            //                         memo.size() + 1];
            // snprintf(buffer, sizeof(format), format.c_str(), title, memo);

            // string query(buffer);
            string query = fmt::format("INSERT INTO memo(title, msg) VALUES(\"{}\", \"{}\");", title, memo);
            conn->exec_query(query);
            cout << "Success" << endl;

            // delete[] buffer;
        }
        else if (input == 2)
        {
            MySQLClient *conn = client;
            string title;
            // string format = "SELECT * FROM memo WHERE title=\"%s\";";
            MYSQL_RES *exec_result;
            MYSQL_ROW row;
            cout << "Search memo" << endl;
            cout << "title: ";
            getline(cin, title);
            // char *buffer = new char[format.size() + title.size() + 1];
            // snprintf(buffer, format.size(), format.c_str(), title.c_str());
            // string query(buffer);
            string query = fmt::format("SELECT * FROM memo WHERE title=\"{}\";", title);
            exec_result = conn->exec_query_result(query);

            if (exec_result)
            {
                if (exec_result == nullptr)
                {
                    cout << "Execute Result is "
                         << "NULL Pointer" << endl;
                }
                else
                {
                    cout << "Execute Result is "
                         << "MYSQL_RES Pointer" << endl;
                    row = mysql_fetch_row(exec_result);
                    cout << "Title: " << row[1] << endl;
                    cout << "memo: " << row[2] << endl;
                }
            }
            else
            {
                cout << "Failed execute query" << endl;
                exit(-1);
            }

            // delete[] buffer;
        }
        else
        {
            cout << "Exited" << endl;
            exit(0);
        }
    }
    return 0;
}