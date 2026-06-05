import { ReactNode, useEffect, useState } from 'react';
import keycloak from './keycloak';

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps): JSX.Element {
  const [authenticated, setAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    keycloak.init({
      onLoad: 'login-required',
      pkceMethod: 'S256',
      checkLoginIframe: false,
    }).then(auth => {
      setAuthenticated(auth);
      setLoading(false);

      // Refresh token 60s before expiry
      const interval = setInterval(() => {
        keycloak.updateToken(60).catch(() => keycloak.login());
      }, 30000);
      return () => clearInterval(interval);
    }).catch(() => {
      setLoading(false);
    });
  }, []);

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh', background: '#0d0d1a', color: '#e0e0e0' }}>
        Authenticating...
      </div>
    );
  }

  if (!authenticated) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh', background: '#0d0d1a', color: '#e0e0e0' }}>
        Login required. Redirecting...
      </div>
    );
  }

  return <>{children}</>;
}

export { keycloak };
