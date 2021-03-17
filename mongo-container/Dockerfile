FROM mongo:4.2

ENV MONGO_INITDB_ROOT_USERNAME=admin
ENV MONGO_INITDB_ROOT_PASSWORD=adm1n_passw0rd

ENV MONGO_INITDB_DATABASE=eve

COPY ./initdb.js /docker-entrypoint-initdb.d/
