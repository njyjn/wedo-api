dropdb 'api-test' --if-exists
createdb 'api-test'
export DATABASE_URL=postgres://{username}@{host}:{port}/api-test