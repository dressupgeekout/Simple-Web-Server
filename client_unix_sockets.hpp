#ifndef SIMPLE_WEB_CLIENT_UNIX_SOCKET_HPP
#define SIMPLE_WEB_CLIENT_UNIX_SOCKET_HPP

#include "client_http.hpp"

namespace SimpleWeb {
    using UNIX_SOCKET = asio::local::stream_protocol::socket;

    template<>
    class Client<UNIX_SOCKET> : public ClientBase<UNIX_SOCKET> {
    public:

        /**
         * Constructs a client object.
         *
         * @param endpoint path to the local unix socket file
         */
        explicit Client<UNIX_SOCKET>(std::string endpoint)
                : ClientBase<asio::local::stream_protocol::socket>("", 0),
                  endpoint(std::move(endpoint)) {
        }

    protected:
        std::shared_ptr<Connection> create_connection() noexcept override {
            return std::make_shared<Connection>(handler_runner, *io_service);
        }

        void connect(const std::shared_ptr<Session> &session) override {
            session->connection->set_timeout(config.timeout_connect);
            session->connection->socket->async_connect(endpoint, [this, session](const error_code &ec) {
                session->connection->cancel_timeout();
                auto lock = session->connection->handler_runner->continue_lock();
                if (!lock)
                    return;
                if (!ec) {
                    this->write(session);
                } else
                    session->callback(ec);
            });
        }

    private:
        std::string endpoint;

    };
} // namespace SimpleWeb

#endif /* SIMPLE_WEB_CLIENT_UNIX_SOCKET_HPP */
