# Source Code(Protobuf 23)

## MessageLite::ParseFromArray(...)

```cpp
bool MessageLite::ParseFromArray(const void* data, int size) {
  return ParseFrom<kParse>(as_string_view(data, size));
}
```

```cpp
template <MessageLite::ParseFlags flags, typename T>
bool MessageLite::ParseFrom(const T& input) {
  if (flags & kParse) Clear();
  constexpr bool alias = (flags & kMergeWithAliasing) != 0;
  return internal::MergeFromImpl<alias>(input, this, flags);
}
```

```cpp
template <bool aliasing>
bool MergeFromImpl(absl::string_view input, MessageLite* msg,
                   MessageLite::ParseFlags parse_flags) {
  const char* ptr;
  internal::ParseContext ctx(io::CodedInputStream::GetDefaultRecursionLimit(),
                             aliasing, &ptr, input);
  ptr = msg->_InternalParse(ptr, &ctx);
  // ctx has an explicit limit set (length of string_view).
  if (PROTOBUF_PREDICT_TRUE(ptr && ctx.EndedAtLimit())) {
    return CheckFieldPresence(ctx, *msg, parse_flags);
  }
  return false;
}
```

```cpp
const char* MessageLite::_InternalParse(const char* ptr,
                                        internal::ParseContext* ctx) {
  auto* data = GetClassData();
  ABSL_DCHECK(data != nullptr);

  if (data->tc_table != nullptr) {
    return internal::TcParser::ParseLoop(this, ptr, ctx, data->tc_table);
  }
  return nullptr;
}
```

```cpp
// Returns true if all required fields are present / have values.
inline bool CheckFieldPresence(const internal::ParseContext& ctx,
                               const MessageLite& msg,
                               MessageLite::ParseFlags parse_flags) {
  (void)ctx;  // Parameter is used by Google-internal code.
  if (PROTOBUF_PREDICT_FALSE((parse_flags & MessageLite::kMergePartial) != 0)) {
    return true;
  }
  return msg.IsInitializedWithErrors();
}
```

## mysql_real_connect corrupted

```cpp
MYSQL *STDCALL mysql_real_connect(MYSQL *mysql, const char *host,
                                  const char *user, const char *passwd,
                                  const char *db, uint port,
                                  const char *unix_socket, ulong client_flag) {
  DBUG_TRACE;
  mysql_async_connect ctx;
  memset(&ctx, 0, sizeof(ctx));

  ctx.mysql = mysql; /*  */
  ctx.host = host;
  ctx.port = port;
  ctx.db = db;
  ctx.user = user;
  ENSURE_EXTENSIONS_PRESENT(&mysql->options);
  /* password will be extracted from mysql options */
  if (mysql->options.extension->client_auth_info[0].password)
    ctx.passwd = mysql->options.extension->client_auth_info[0].password;
  else
    ctx.passwd = passwd;
  ctx.unix_socket = unix_socket;
  if (0 != (client_flag & CLIENT_NO_SCHEMA)) {
    fprintf(stderr,
            "WARNING: CLIENT_NO_SCHEMA is deprecated and will be removed in a "
            "future version.\n");
  }
  mysql->options.client_flag |= client_flag;
  ctx.client_flag = mysql->options.client_flag;
  ctx.ssl_state = SSL_NONE;
  return (*mysql->methods->connect_method)(&ctx);
}
```

```c
MYSQL *csi_connect(mysql_async_connect *ctx) {
  assert(ctx);
  ctx->state_function = cs::cssm_begin_connect;
  return connect_helper(ctx);
}
```

```cpp
MYSQL_METHODS mysql_methods = {
    csi_connect,       csi_read_query_result, csi_advanced_command,
    csi_read_rows,     csi_use_result,        csi_fetch_row,
    csi_fetch_lengths, csi_flush_use_result,  csi_read_change_user_result,
#if !defined(MYSQL_SERVER) && !defined(MYSQL_COMPONENT)
    nullptr,  // csi_list_fields,
    nullptr,  // csi_read_prepare_result,
    nullptr,  // csi_stmt_execute,
    nullptr,  // csi_read_binary_rows,
    nullptr,  // csi_unbuffered_fetch,
    nullptr,  // csi_free_embedded_thd,
    nullptr,  // csi_read_statistics,
    nullptr,  // csi_next_result,
    nullptr,  // csi_read_rows_from_cursor
#endif        // ! MYSQL_SERVER
    nullptr,  /* read_query_result_nonblocking */
    nullptr,  /* advanced_command_nonblocking */
    nullptr,  /* read_rows_nonblocking */
    nullptr,  /* flush_use_result_nonblocking */
    nullptr,  /* next_result_nonblocking */
    nullptr,  /* read_change_user_result_nonblocking */
};
```

```cpp
mysql_state_machine_status cssm_begin_connect(mysql_async_connect *ctx) {
  MYSQL *mysql = ctx->mysql;
  auto mcs_extn = MYSQL_COMMAND_SERVICE_EXTN(mysql);
  assert(mcs_extn);
  const char *host = ctx->host;
  const char *user = ctx->user;
  const char *db = ctx->db;
  MYSQL_THD thd;
  my_h_service h_command_consumer = nullptr;
  my_h_service h_command_consumer_srv = nullptr;

  MYSQL_SESSION mysql_session = nullptr;
  if (mcs_extn->mcs_thd == nullptr || mcs_extn->session_svc == nullptr) {
    /*
     Avoid possibility of nested txn in the current thd.
     If it is called, for example from a UDF.
    */
    my_service<SERVICE_TYPE(mysql_admin_session)> service(
        "mysql_admin_session.mysql_server", srv_registry);
    if (service.is_valid()) {
      mysql_session = service->open(nullptr, ctx);
      if (mysql_session == nullptr) return STATE_MACHINE_FAILED;
    } else
      return STATE_MACHINE_FAILED;
    thd = mysql_session->get_thd();
    mcs_extn->is_thd_associated = false;
    Security_context_handle sc;
    if (mysql_security_context_imp::get(thd, &sc)) return STATE_MACHINE_FAILED;
    if (mysql_security_context_imp::lookup(sc, user, host, nullptr, db))
      return STATE_MACHINE_FAILED;
    mcs_extn->mcs_thd = thd;
    mysql->thd = thd;
    mcs_extn->session_svc = mysql_session;
  } else {
    mysql->thd = reinterpret_cast<void *>(mcs_extn->mcs_thd);
  }
  /*
    These references might be created in mysql_command_services_imp::set api.
    If not, we will create here.
  */
  if (mcs_extn->command_consumer_services == nullptr) {
    /*
      Provide default implementations for mysql command consumer services
      and will be released in close() api.
    */
    mcs_extn->command_consumer_services = new mysql_command_consumer_refs();
  }
  mysql_command_consumer_refs *consumer_refs =
      (mysql_command_consumer_refs *)mcs_extn->command_consumer_services;
  /* The above new allocation failed */
  if (consumer_refs == nullptr) return STATE_MACHINE_FAILED;
  /* If the service is not acquired by mysql_command_services_imp::set api,
     then it will be acquired below. The same will be applicable for all
     other below services. */
  if (consumer_refs->factory_srv == nullptr) {
    if (srv_registry->acquire("mysql_text_consumer_factory_v1.mysql_server",
                              &h_command_consumer))
      return STATE_MACHINE_FAILED;
    else
      consumer_refs->factory_srv = reinterpret_cast<SERVICE_TYPE_NO_CONST(
          mysql_text_consumer_factory_v1) *>(h_command_consumer);
  }

  if (consumer_refs->metadata_srv == nullptr) {
    if (srv_registry->acquire_related("mysql_text_consumer_metadata_v1",
                                      h_command_consumer,
                                      &h_command_consumer_srv))
      return STATE_MACHINE_FAILED;
    else
      consumer_refs->metadata_srv = reinterpret_cast<SERVICE_TYPE_NO_CONST(
          mysql_text_consumer_metadata_v1) *>(h_command_consumer_srv);
  }

  if (consumer_refs->row_factory_srv == nullptr) {
    if (srv_registry->acquire_related("mysql_text_consumer_row_factory_v1",
                                      h_command_consumer,
                                      &h_command_consumer_srv))
      return STATE_MACHINE_FAILED;
    else
      consumer_refs->row_factory_srv = reinterpret_cast<SERVICE_TYPE_NO_CONST(
          mysql_text_consumer_row_factory_v1) *>(h_command_consumer_srv);
  }

  if (consumer_refs->error_srv == nullptr) {
    if (srv_registry->acquire_related("mysql_text_consumer_error_v1",
                                      h_command_consumer,
                                      &h_command_consumer_srv))
      return STATE_MACHINE_FAILED;
    else
      consumer_refs->error_srv = reinterpret_cast<SERVICE_TYPE_NO_CONST(
          mysql_text_consumer_error_v1) *>(h_command_consumer_srv);
  }

  if (consumer_refs->get_null_srv == nullptr) {
    if (srv_registry->acquire_related("mysql_text_consumer_get_null_v1",
                                      h_command_consumer,
                                      &h_command_consumer_srv))
      return STATE_MACHINE_FAILED;
    else
      consumer_refs->get_null_srv = reinterpret_cast<SERVICE_TYPE_NO_CONST(
          mysql_text_consumer_get_null_v1) *>(h_command_consumer_srv);
  }

  if (consumer_refs->get_integer_srv == nullptr) {
    if (srv_registry->acquire_related("mysql_text_consumer_get_integer_v1",
                                      h_command_consumer,
                                      &h_command_consumer_srv))
      return STATE_MACHINE_FAILED;
    else
      consumer_refs->get_integer_srv = reinterpret_cast<SERVICE_TYPE_NO_CONST(
          mysql_text_consumer_get_integer_v1) *>(h_command_consumer_srv);
  }

  if (consumer_refs->get_longlong_srv == nullptr) {
    if (srv_registry->acquire_related("mysql_text_consumer_get_longlong_v1",
                                      h_command_consumer,
                                      &h_command_consumer_srv))
      return STATE_MACHINE_FAILED;
    else
      consumer_refs->get_longlong_srv = reinterpret_cast<SERVICE_TYPE_NO_CONST(
          mysql_text_consumer_get_longlong_v1) *>(h_command_consumer_srv);
  }

  if (consumer_refs->get_decimal_srv == nullptr) {
    if (srv_registry->acquire_related("mysql_text_consumer_get_decimal_v1",
                                      h_command_consumer,
                                      &h_command_consumer_srv))
      return STATE_MACHINE_FAILED;
    else
      consumer_refs->get_decimal_srv = reinterpret_cast<SERVICE_TYPE_NO_CONST(
          mysql_text_consumer_get_decimal_v1) *>(h_command_consumer_srv);
  }

  if (consumer_refs->get_double_srv == nullptr) {
    if (srv_registry->acquire_related("mysql_text_consumer_get_double_v1",
                                      h_command_consumer,
                                      &h_command_consumer_srv))
      return STATE_MACHINE_FAILED;
    else
      consumer_refs->get_double_srv = reinterpret_cast<SERVICE_TYPE_NO_CONST(
          mysql_text_consumer_get_double_v1) *>(h_command_consumer_srv);
  }

  if (consumer_refs->get_date_time_srv == nullptr) {
    if (srv_registry->acquire_related("mysql_text_consumer_get_date_time_v1",
                                      h_command_consumer,
                                      &h_command_consumer_srv))
      return STATE_MACHINE_FAILED;
    else
      consumer_refs->get_date_time_srv = reinterpret_cast<SERVICE_TYPE_NO_CONST(
          mysql_text_consumer_get_date_time_v1) *>(h_command_consumer_srv);
  }

  if (consumer_refs->get_string_srv == nullptr) {
    if (srv_registry->acquire_related("mysql_text_consumer_get_string_v1",
                                      h_command_consumer,
                                      &h_command_consumer_srv))
      return STATE_MACHINE_FAILED;
    else
      consumer_refs->get_string_srv = reinterpret_cast<SERVICE_TYPE_NO_CONST(
          mysql_text_consumer_get_string_v1) *>(h_command_consumer_srv);
  }

  if (consumer_refs->client_capabilities_srv == nullptr) {
    if (srv_registry->acquire_related(
            "mysql_text_consumer_client_capabilities_v1", h_command_consumer,
            &h_command_consumer_srv))
      return STATE_MACHINE_FAILED;
    else
      consumer_refs->client_capabilities_srv =
          reinterpret_cast<SERVICE_TYPE_NO_CONST(
              mysql_text_consumer_client_capabilities_v1) *>(
              h_command_consumer_srv);
  }
  mysql->client_flag = 0; /* For handshake */
  mysql->server_status = SERVER_STATUS_AUTOCOMMIT;
  return STATE_MACHINE_DONE;
}
```

```cpp
MYSQL *connect_helper(mysql_async_connect *ctx) {
  mysql_state_machine_status status;
  auto mysql = ctx->mysql;
  mysql->options.client_flag |= ctx->client_flag;
  do {
    status = ctx->state_function(ctx);
  } while (status != STATE_MACHINE_FAILED && status != STATE_MACHINE_DONE);

  if (status == STATE_MACHINE_DONE) {
    DBUG_PRINT("exit", ("Mysql handler: %p", mysql));
    return ctx->mysql;
  }

  DBUG_PRINT("error", ("message: %u/%s (%s)", mysql->net.last_errno,
                       mysql->net.sqlstate, mysql->net.last_error));
  {
    /* Free alloced memory */
    end_server(mysql);
    mysql_close_free(mysql);
    if (!(ctx->client_flag & CLIENT_REMEMBER_OPTIONS))
      mysql_close_free_options(mysql);
    if (ctx->scramble_buffer_allocated) my_free(ctx->scramble_buffer);
  }
  return nullptr;
}
```

```c
/** set some default attributes */
static int set_connect_attributes(MYSQL *mysql, char *buff, size_t buf_len) {
  DBUG_TRACE;
  int rc = 0;

  /*
    Clean up any values set by the client code. We want these options as
    consistent as possible
  */
  rc += mysql_options(mysql, MYSQL_OPT_CONNECT_ATTR_DELETE, "_client_name");
  rc += mysql_options(mysql, MYSQL_OPT_CONNECT_ATTR_DELETE, "_os");
  rc += mysql_options(mysql, MYSQL_OPT_CONNECT_ATTR_DELETE, "_platform");
  rc += mysql_options(mysql, MYSQL_OPT_CONNECT_ATTR_DELETE, "_pid");
  rc += mysql_options(mysql, MYSQL_OPT_CONNECT_ATTR_DELETE, "_thread");
  rc += mysql_options(mysql, MYSQL_OPT_CONNECT_ATTR_DELETE, "_client_version");

  /*
   Now let's set up some values
  */
  rc += mysql_options4(mysql, MYSQL_OPT_CONNECT_ATTR_ADD, "_client_name",
                       "libmysql");
  rc += mysql_options4(mysql, MYSQL_OPT_CONNECT_ATTR_ADD, "_client_version",
                       PACKAGE_VERSION);
  rc += mysql_options4(mysql, MYSQL_OPT_CONNECT_ATTR_ADD, "_os", SYSTEM_TYPE);
  rc += mysql_options4(mysql, MYSQL_OPT_CONNECT_ATTR_ADD, "_platform",
                       MACHINE_TYPE);

  return rc > 0 ? 1 : 0;
}
```

```cpp
int STDCALL mysql_options(MYSQL *mysql, enum mysql_option option,
                          const void *arg) {
  DBUG_TRACE;
  DBUG_PRINT("enter", ("option: %d", (int)option));
  switch (option) {
    case MYSQL_OPT_CONNECT_TIMEOUT:
      mysql->options.connect_timeout = *static_cast<const uint *>(arg);
      break;
    case MYSQL_OPT_READ_TIMEOUT:
      mysql->options.read_timeout = *static_cast<const uint *>(arg);
      break;
    case MYSQL_OPT_WRITE_TIMEOUT:
      mysql->options.write_timeout = *static_cast<const uint *>(arg);
      break;
    case MYSQL_OPT_COMPRESS:
      mysql->options.compress = true; /* Remember for connect */
      mysql->options.client_flag |= CLIENT_COMPRESS;
      break;
    case MYSQL_OPT_NAMED_PIPE: /* This option is deprecated */
      mysql->options.protocol = MYSQL_PROTOCOL_PIPE; /* Force named pipe */
      break;
    case MYSQL_OPT_LOCAL_INFILE: /* Allow LOAD DATA LOCAL ?*/
      if (!arg || (*static_cast<const uint *>(arg) != 0))
        mysql->options.client_flag |= CLIENT_LOCAL_FILES;
      else
        mysql->options.client_flag &= ~CLIENT_LOCAL_FILES;
      break;
    case MYSQL_INIT_COMMAND:
      add_init_command(&mysql->options, static_cast<const char *>(arg));
      break;
    case MYSQL_READ_DEFAULT_FILE:
      my_free(mysql->options.my_cnf_file);
      mysql->options.my_cnf_file =
          my_strdup(key_memory_mysql_options, static_cast<const char *>(arg),
                    MYF(MY_WME));
      break;
    case MYSQL_READ_DEFAULT_GROUP:
      my_free(mysql->options.my_cnf_group);
      mysql->options.my_cnf_group =
          my_strdup(key_memory_mysql_options, static_cast<const char *>(arg),
                    MYF(MY_WME));
      break;
    case MYSQL_SET_CHARSET_DIR:
      my_free(mysql->options.charset_dir);
      mysql->options.charset_dir =
          my_strdup(key_memory_mysql_options, static_cast<const char *>(arg),
                    MYF(MY_WME));
      break;
    case MYSQL_SET_CHARSET_NAME:
      my_free(mysql->options.charset_name);
      mysql->options.charset_name =
          my_strdup(key_memory_mysql_options, static_cast<const char *>(arg),
                    MYF(MY_WME));
      break;
    case MYSQL_OPT_PROTOCOL:
      mysql->options.protocol = *static_cast<const uint *>(arg);
      break;
    case MYSQL_SHARED_MEMORY_BASE_NAME:
#if defined(_WIN32)
      my_free(mysql->options.shared_memory_base_name);

      mysql->options.shared_memory_base_name =
          my_strdup(key_memory_mysql_options, static_cast<const char *>(arg),
                    MYF(MY_WME));
#endif
      break;
    case MYSQL_REPORT_DATA_TRUNCATION:
      mysql->options.report_data_truncation = *static_cast<const bool *>(arg);
      break;
    case MYSQL_OPT_RECONNECT:
      fprintf(stderr,
              "WARNING: MYSQL_OPT_RECONNECT is deprecated and will be "
              "removed in a future version.\n");
      mysql->reconnect = *static_cast<const bool *>(arg);
      break;
    case MYSQL_OPT_BIND:
      my_free(mysql->options.bind_address);
      mysql->options.bind_address =
          my_strdup(key_memory_mysql_options, static_cast<const char *>(arg),
                    MYF(MY_WME));
      break;
    case MYSQL_PLUGIN_DIR:
      EXTENSION_SET_STRING(&mysql->options, plugin_dir,
                           static_cast<const char *>(arg));
      break;
    case MYSQL_DEFAULT_AUTH:
      EXTENSION_SET_STRING(&mysql->options, default_auth,
                           static_cast<const char *>(arg));
      break;
    case MYSQL_OPT_SSL_KEY:
      if (mysql->options.ssl_key) my_free(mysql->options.ssl_key);
      mysql->options.ssl_key =
          set_ssl_option_unpack_path(static_cast<const char *>(arg));
      break;
    case MYSQL_OPT_SSL_CERT:
      if (mysql->options.ssl_cert) my_free(mysql->options.ssl_cert);
      mysql->options.ssl_cert =
          set_ssl_option_unpack_path(static_cast<const char *>(arg));
      break;
    case MYSQL_OPT_SSL_CA:
      if (mysql->options.ssl_ca) my_free(mysql->options.ssl_ca);
      mysql->options.ssl_ca =
          set_ssl_option_unpack_path(static_cast<const char *>(arg));
      break;
    case MYSQL_OPT_SSL_CAPATH:
      if (mysql->options.ssl_capath) my_free(mysql->options.ssl_capath);
      mysql->options.ssl_capath =
          set_ssl_option_unpack_path(static_cast<const char *>(arg));
      break;
    case MYSQL_OPT_SSL_CIPHER:
      SET_OPTION(ssl_cipher, static_cast<const char *>(arg));
      break;
    case MYSQL_OPT_TLS_CIPHERSUITES:
      EXTENSION_SET_STRING(&mysql->options, tls_ciphersuites,
                           static_cast<const char *>(arg));
      break;
    case MYSQL_OPT_SSL_CRL:
      if (mysql->options.extension)
        my_free(mysql->options.extension->ssl_crl);
      else
        ALLOCATE_EXTENSIONS(&mysql->options);
      mysql->options.extension->ssl_crl =
          set_ssl_option_unpack_path(static_cast<const char *>(arg));
      break;
    case MYSQL_OPT_SSL_CRLPATH:
      if (mysql->options.extension)
        my_free(mysql->options.extension->ssl_crlpath);
      else
        ALLOCATE_EXTENSIONS(&mysql->options);
      mysql->options.extension->ssl_crlpath =
          set_ssl_option_unpack_path(static_cast<const char *>(arg));
      break;
    case MYSQL_OPT_TLS_VERSION:
      EXTENSION_SET_STRING(&mysql->options, tls_version,
                           static_cast<const char *>(arg));
      if ((mysql->options.extension->ssl_ctx_flags = process_tls_version(
               mysql->options.extension->tls_version)) == -1)
        return 1;
      break;
    case MYSQL_OPT_SSL_FIPS_MODE: { /* This option is deprecated */
      fprintf(stderr,
              "WARNING: MYSQL_OPT_SSL_FIPS_MODE is deprecated and will be "
              "removed in a future version.\n");
      char ssl_err_string[OPENSSL_ERROR_LENGTH] = {'\0'};
      ENSURE_EXTENSIONS_PRESENT(&mysql->options);
      mysql->options.extension->ssl_fips_mode =
          *static_cast<const ulong *>(arg);
      if (set_fips_mode(mysql->options.extension->ssl_fips_mode,
                        ssl_err_string)) {
        DBUG_PRINT("error", ("fips mode set error %s:", ssl_err_string));
        set_mysql_extended_error(
            mysql, CR_SSL_FIPS_MODE_ERR, unknown_sqlstate,
            "Set Fips mode ON/STRICT failed, detail: '%s'.", ssl_err_string);
        return 1;
      }
    } break;
    case MYSQL_OPT_SSL_MODE:
      ENSURE_EXTENSIONS_PRESENT(&mysql->options);
      mysql->options.extension->ssl_mode = *static_cast<const uint *>(arg);
      if (mysql->options.extension->ssl_mode == SSL_MODE_VERIFY_IDENTITY)
        mysql->options.client_flag |= CLIENT_SSL_VERIFY_SERVER_CERT;
      else
        mysql->options.client_flag &= ~CLIENT_SSL_VERIFY_SERVER_CERT;
      break;
    case MYSQL_SERVER_PUBLIC_KEY:
      EXTENSION_SET_STRING(&mysql->options, server_public_key_path,
                           static_cast<const char *>(arg));
      break;

    case MYSQL_OPT_GET_SERVER_PUBLIC_KEY:
      ENSURE_EXTENSIONS_PRESENT(&mysql->options);
      mysql->options.extension->get_server_public_key =
          *static_cast<const bool *>(arg);
      break;

    case MYSQL_OPT_CONNECT_ATTR_RESET:
      ENSURE_EXTENSIONS_PRESENT(&mysql->options);
      if (mysql->options.extension->connection_attributes) {
        delete mysql->options.extension->connection_attributes;
        mysql->options.extension->connection_attributes = nullptr;
        mysql->options.extension->connection_attributes_length = 0;
      }
      break;
    case MYSQL_OPT_CONNECT_ATTR_DELETE:
      ENSURE_EXTENSIONS_PRESENT(&mysql->options);
      if (mysql->options.extension->connection_attributes) {
        string key = arg ? pointer_cast<const char *>(arg) : "";

        if (!key.empty()) {
          auto it =
              mysql->options.extension->connection_attributes->hash.find(key);
          if (it !=
              mysql->options.extension->connection_attributes->hash.end()) {
            const string &attr_key = it->first;
            const string &attr_value = it->second;
            mysql->options.extension->connection_attributes_length -=
                get_length_store_length(attr_key.size()) + attr_key.size() +
                get_length_store_length(attr_value.size()) + attr_value.size();

            mysql->options.extension->connection_attributes->hash.erase(it);
          }
        }
      }
      break;
    case MYSQL_ENABLE_CLEARTEXT_PLUGIN:
      ENSURE_EXTENSIONS_PRESENT(&mysql->options);
      mysql->options.extension->enable_cleartext_plugin =
          *static_cast<const bool *>(arg);
      break;
    case MYSQL_OPT_RETRY_COUNT:
      ENSURE_EXTENSIONS_PRESENT(&mysql->options);
      mysql->options.extension->retry_count = *static_cast<const uint *>(arg);
      break;
    case MYSQL_OPT_CAN_HANDLE_EXPIRED_PASSWORDS:
      if (*static_cast<const bool *>(arg))
        mysql->options.client_flag |= CLIENT_CAN_HANDLE_EXPIRED_PASSWORDS;
      else
        mysql->options.client_flag &= ~CLIENT_CAN_HANDLE_EXPIRED_PASSWORDS;
      break;

    case MYSQL_OPT_MAX_ALLOWED_PACKET:
      if (mysql)
        mysql->options.max_allowed_packet = *static_cast<const ulong *>(arg);
      else
        g_max_allowed_packet = *static_cast<const ulong *>(arg);
      break;

    case MYSQL_OPT_NET_BUFFER_LENGTH:
      g_net_buffer_length = *static_cast<const ulong *>(arg);
      break;

    case MYSQL_OPT_OPTIONAL_RESULTSET_METADATA:
      if (*static_cast<const bool *>(arg))
        mysql->options.client_flag |= CLIENT_OPTIONAL_RESULTSET_METADATA;
      else
        mysql->options.client_flag &= ~CLIENT_OPTIONAL_RESULTSET_METADATA;
      break;

    case MYSQL_OPT_COMPRESSION_ALGORITHMS: {
      std::string compress_option(static_cast<const char *>(arg));
      std::vector<std::string> list;
      parse_compression_algorithms_list(compress_option, list);
      ENSURE_EXTENSIONS_PRESENT(&mysql->options);
      mysql->options.extension->connection_compressed = true;
      mysql->options.client_flag &=
          ~(CLIENT_COMPRESS | CLIENT_ZSTD_COMPRESSION_ALGORITHM);
      mysql->options.compress = false;
      auto it = list.begin();
      unsigned int cnt = 0;
      while (it != list.end() && cnt < COMPRESSION_ALGORITHM_COUNT_MAX) {
        std::string value = *it;
        switch (get_compression_algorithm(value)) {
          case enum_compression_algorithm::MYSQL_ZLIB:
            mysql->options.client_flag |= CLIENT_COMPRESS;
            mysql->options.compress = true;
            break;
          case enum_compression_algorithm::MYSQL_ZSTD:
            mysql->options.client_flag |= CLIENT_ZSTD_COMPRESSION_ALGORITHM;
            mysql->options.compress = true;
            break;
          case enum_compression_algorithm::MYSQL_UNCOMPRESSED:
            mysql->options.extension->connection_compressed = false;
            break;
          case enum_compression_algorithm::MYSQL_INVALID:
            break;  // report error
        }
        it++;
        cnt++;
      }
      if (cnt)
        EXTENSION_SET_STRING(&mysql->options, compression_algorithm,
                             static_cast<const char *>(arg));
      mysql->options.extension->total_configured_compression_algorithms = cnt;
    } break;
    case MYSQL_OPT_ZSTD_COMPRESSION_LEVEL:
      ENSURE_EXTENSIONS_PRESENT(&mysql->options);
      mysql->options.extension->zstd_compression_level =
          *static_cast<const unsigned int *>(arg);
      break;

    case MYSQL_OPT_LOAD_DATA_LOCAL_DIR:
      if (set_load_data_local_infile_option(mysql,
                                            static_cast<const char *>(arg)))
        return 1;
      break;
    case MYSQL_OPT_SSL_SESSION_DATA:
      EXTENSION_SET_STRING(&mysql->options, ssl_session_data,
                           static_cast<const char *>(arg));
      break;
    default:
      return 1;
  }
  return 0;
}
```

```cpp
Vio::Vio(uint flags) {
  mysql_socket = MYSQL_INVALID_SOCKET;
  local = sockaddr_storage();
  remote = sockaddr_storage();
#ifdef USE_PPOLL_IN_VIO
  sigemptyset(&signal_mask);
#elif defined(HAVE_KQUEUE)
  kq_fd = -1;
#endif
  if (flags & VIO_BUFFERED_READ)
    read_buffer = (char *)my_malloc(key_memory_vio_read_buffer,
                                    VIO_READ_BUFFER_SIZE, MYF(MY_WME));
}
```

```cpp
int STDCALL mysql_get_option(MYSQL *mysql, enum mysql_option option,
                             const void *arg) {
  DBUG_TRACE;
  DBUG_PRINT("enter", ("option: %d", (int)option));

  if (!arg) return 1;

  switch (option) {
    case MYSQL_OPT_CONNECT_TIMEOUT:
      *(const_cast<uint *>(static_cast<const uint *>(arg))) =
          mysql->options.connect_timeout;
      break;
    case MYSQL_OPT_READ_TIMEOUT:
      *(const_cast<uint *>(static_cast<const uint *>(arg))) =
          mysql->options.read_timeout;
      break;
    case MYSQL_OPT_WRITE_TIMEOUT:
      *(const_cast<uint *>(static_cast<const uint *>(arg))) =
          mysql->options.write_timeout;
      break;
    case MYSQL_OPT_COMPRESS:
      *(const_cast<bool *>(static_cast<const bool *>(arg))) =
          mysql->options.compress;
      break;
    case MYSQL_OPT_LOCAL_INFILE: /* Allow LOAD DATA LOCAL ?*/
      *(const_cast<uint *>(static_cast<const uint *>(arg))) =
          (mysql->options.client_flag & CLIENT_LOCAL_FILES) != 0;
      break;
    case MYSQL_READ_DEFAULT_FILE:
      *(static_cast<char **>(const_cast<void *>(arg))) =
          mysql->options.my_cnf_file;
      break;
    case MYSQL_READ_DEFAULT_GROUP:
      *(static_cast<char **>(const_cast<void *>(arg))) =
          mysql->options.my_cnf_group;
      break;
    case MYSQL_SET_CHARSET_DIR:
      *(static_cast<char **>(const_cast<void *>(arg))) =
          mysql->options.charset_dir;
      break;
    case MYSQL_SET_CHARSET_NAME:
      *(static_cast<char **>(const_cast<void *>(arg))) =
          mysql->options.charset_name;
      break;
    case MYSQL_OPT_PROTOCOL:
      *(const_cast<uint *>(static_cast<const uint *>(arg))) =
          mysql->options.protocol;
      break;
    case MYSQL_SHARED_MEMORY_BASE_NAME:
#if defined(_WIN32)
      *(static_cast<char **>(const_cast<void *>(arg))) =
          mysql->options.shared_memory_base_name;
#else
      *(static_cast<char **>(const_cast<void *>(arg))) = const_cast<char *>("");
#endif
      break;
    case MYSQL_REPORT_DATA_TRUNCATION:
      *(const_cast<bool *>(static_cast<const bool *>(arg))) =
          mysql->options.report_data_truncation;
      break;
    case MYSQL_OPT_RECONNECT:
      fprintf(stderr,
              "WARNING: MYSQL_OPT_RECONNECT is deprecated and will be "
              "removed in a future version.\n");
      *(const_cast<bool *>(static_cast<const bool *>(arg))) = mysql->reconnect;
      break;
    case MYSQL_OPT_BIND:
      *(static_cast<char **>(const_cast<void *>(arg))) =
          mysql->options.bind_address;
      break;
    case MYSQL_OPT_SSL_MODE:
      *(const_cast<uint *>(static_cast<const uint *>(arg))) =
          mysql->options.extension ? mysql->options.extension->ssl_mode : 0;
      break;
    case MYSQL_OPT_SSL_FIPS_MODE: /* This option is deprecated */
      *(const_cast<uint *>(static_cast<const uint *>(arg))) =
          mysql->options.extension ? mysql->options.extension->ssl_fips_mode
                                   : 0;
      break;
    case MYSQL_PLUGIN_DIR:
      *(static_cast<char **>(const_cast<void *>(arg))) =
          mysql->options.extension ? mysql->options.extension->plugin_dir
                                   : nullptr;
      break;
    case MYSQL_DEFAULT_AUTH:
      *(static_cast<char **>(const_cast<void *>(arg))) =
          mysql->options.extension ? mysql->options.extension->default_auth
                                   : nullptr;
      break;
    case MYSQL_OPT_SSL_KEY:
      *(static_cast<char **>(const_cast<void *>(arg))) = mysql->options.ssl_key;
      break;
    case MYSQL_OPT_SSL_CERT:
      *(static_cast<char **>(const_cast<void *>(arg))) =
          mysql->options.ssl_cert;
      break;
    case MYSQL_OPT_SSL_CA:
      *(static_cast<char **>(const_cast<void *>(arg))) = mysql->options.ssl_ca;
      break;
    case MYSQL_OPT_SSL_CAPATH:
      *(static_cast<char **>(const_cast<void *>(arg))) =
          mysql->options.ssl_capath;
      break;
    case MYSQL_OPT_SSL_CIPHER:
      *(static_cast<char **>(const_cast<void *>(arg))) =
          mysql->options.ssl_cipher;
      break;
    case MYSQL_OPT_TLS_CIPHERSUITES:
      *(static_cast<char **>(const_cast<void *>(arg))) =
          mysql->options.extension ? mysql->options.extension->tls_ciphersuites
                                   : nullptr;
      break;
    case MYSQL_OPT_RETRY_COUNT:
      *(const_cast<uint *>(static_cast<const uint *>(arg))) =
          mysql->options.extension ? mysql->options.extension->retry_count : 1;
      break;
    case MYSQL_OPT_TLS_VERSION:
      *(static_cast<char **>(const_cast<void *>(arg))) =
          mysql->options.extension ? mysql->options.extension->tls_version
                                   : nullptr;
      break;
    case MYSQL_OPT_SSL_CRL:
      *(static_cast<char **>(const_cast<void *>(arg))) =
          mysql->options.extension ? mysql->options.extension->ssl_crl
                                   : nullptr;
      break;
    case MYSQL_OPT_SSL_CRLPATH:
      *(static_cast<char **>(const_cast<void *>(arg))) =
          mysql->options.extension ? mysql->options.extension->ssl_crlpath
                                   : nullptr;
      break;
    case MYSQL_SERVER_PUBLIC_KEY:
      *(static_cast<char **>(const_cast<void *>(arg))) =
          mysql->options.extension
              ? mysql->options.extension->server_public_key_path
              : nullptr;
      break;
    case MYSQL_OPT_GET_SERVER_PUBLIC_KEY:
      *(const_cast<bool *>(static_cast<const bool *>(arg))) =
          mysql->options.extension &&
          mysql->options.extension->get_server_public_key;
      break;
    case MYSQL_ENABLE_CLEARTEXT_PLUGIN:
      *(const_cast<bool *>(static_cast<const bool *>(arg))) =
          mysql->options.extension &&
          mysql->options.extension->enable_cleartext_plugin;
      break;
    case MYSQL_OPT_CAN_HANDLE_EXPIRED_PASSWORDS:
      *(const_cast<bool *>(static_cast<const bool *>(arg))) =
          (mysql->options.client_flag & CLIENT_CAN_HANDLE_EXPIRED_PASSWORDS) !=
          0;
      break;

    case MYSQL_OPT_MAX_ALLOWED_PACKET:
      if (mysql)
        *(const_cast<ulong *>(static_cast<const ulong *>(arg))) =
            mysql->options.max_allowed_packet;
      else
        *(const_cast<ulong *>(static_cast<const ulong *>(arg))) =
            g_max_allowed_packet;
      break;

    case MYSQL_OPT_NET_BUFFER_LENGTH:
      *(const_cast<ulong *>(static_cast<const ulong *>(arg))) =
          g_net_buffer_length;
      break;

    case MYSQL_OPT_OPTIONAL_RESULTSET_METADATA:
      *(const_cast<bool *>(static_cast<const bool *>(arg))) =
          (mysql->options.client_flag & CLIENT_OPTIONAL_RESULTSET_METADATA) !=
          0;
      break;
    case MYSQL_OPT_LOAD_DATA_LOCAL_DIR:
      *(static_cast<char **>(const_cast<void *>(arg))) =
          mysql->options.extension ? mysql->options.extension->load_data_dir
                                   : nullptr;
      break;
    case MYSQL_OPT_SSL_SESSION_DATA:
      *(static_cast<char **>(const_cast<void *>(arg))) =
          mysql->options.extension
              ? static_cast<char *>(mysql->options.extension->ssl_session_data)
              : nullptr;
      break;

    case MYSQL_OPT_NAMED_PIPE:          /* This option is deprecated */
    case MYSQL_INIT_COMMAND:            /* Cumulative */
    case MYSQL_OPT_CONNECT_ATTR_RESET:  /* Cumulative */
    case MYSQL_OPT_CONNECT_ATTR_DELETE: /* Cumulative */
    default:
      return 1;
  }
  return 0;
}
```
