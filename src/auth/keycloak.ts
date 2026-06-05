import Keycloak from 'keycloak-js';

const keycloak = new Keycloak({
  url: 'http://localhost:8080',
  realm: 'flowind',
  clientId: 'flowind-frontend',
});

export default keycloak;
