/**
 * Testes para o componente App
 */
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import App from '../App';

// Mock do fetch global
global.fetch = vi.fn();

// Mock do localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};
global.localStorage = localStorageMock;

describe('App Component', () => {
  beforeEach(() => {
    // Limpar mocks antes de cada teste
    vi.clearAllMocks();
    localStorageMock.getItem.mockReturnValue(null);
  });

  test('renders login form when not authenticated', () => {
    render(<App />);
    
    expect(screen.getByText('Beepy')).toBeInTheDocument();
    expect(screen.getByText('Sistema de Indicações e Comissões')).toBeInTheDocument();
    expect(screen.getByLabelText('Email')).toBeInTheDocument();
    expect(screen.getByLabelText('Senha')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /entrar/i })).toBeInTheDocument();
  });

  test('shows loading state initially', () => {
    render(<App />);
    
    expect(screen.getByText('Carregando...')).toBeInTheDocument();
  });

  test('displays test credentials', () => {
    render(<App />);
    
    expect(screen.getByText('Credenciais de teste:')).toBeInTheDocument();
    expect(screen.getByText(/admin@beepy.com/)).toBeInTheDocument();
    expect(screen.getByText(/embaixadora@teste.com/)).toBeInTheDocument();
  });

  test('handles email input change', () => {
    render(<App />);
    
    const emailInput = screen.getByLabelText('Email');
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    
    expect(emailInput.value).toBe('test@example.com');
  });

  test('handles password input change', () => {
    render(<App />);
    
    const passwordInput = screen.getByLabelText('Senha');
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    
    expect(passwordInput.value).toBe('password123');
  });

  test('toggles password visibility', () => {
    render(<App />);
    
    const passwordInput = screen.getByLabelText('Senha');
    const toggleButton = screen.getByRole('button', { name: '' }); // Botão de toggle
    
    expect(passwordInput.type).toBe('password');
    
    fireEvent.click(toggleButton);
    expect(passwordInput.type).toBe('text');
    
    fireEvent.click(toggleButton);
    expect(passwordInput.type).toBe('password');
  });

  test('handles successful login', async () => {
    const mockResponse = {
      access_token: 'fake-token',
      user: {
        id: 1,
        name: 'Admin User',
        email: 'admin@beepy.com',
        role: 'admin'
      }
    };

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    });

    render(<App />);
    
    const emailInput = screen.getByLabelText('Email');
    const passwordInput = screen.getByLabelText('Senha');
    const submitButton = screen.getByRole('button', { name: /entrar/i });
    
    fireEvent.change(emailInput, { target: { value: 'admin@beepy.com' } });
    fireEvent.change(passwordInput, { target: { value: 'admin123' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:10000/auth/login',
        expect.objectContaining({
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email: 'admin@beepy.com',
            password: 'admin123'
          }),
        })
      );
    });

    expect(localStorageMock.setItem).toHaveBeenCalledWith('access_token', 'fake-token');
  });

  test('handles login error', async () => {
    const mockErrorResponse = {
      error: 'Credenciais inválidas'
    };

    fetch.mockResolvedValueOnce({
      ok: false,
      json: async () => mockErrorResponse,
    });

    // Mock do alert
    window.alert = vi.fn();

    render(<App />);
    
    const emailInput = screen.getByLabelText('Email');
    const passwordInput = screen.getByLabelText('Senha');
    const submitButton = screen.getByRole('button', { name: /entrar/i });
    
    fireEvent.change(emailInput, { target: { value: 'wrong@email.com' } });
    fireEvent.change(passwordInput, { target: { value: 'wrongpassword' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(window.alert).toHaveBeenCalledWith('Credenciais inválidas');
    });
  });

  test('handles network error during login', async () => {
    fetch.mockRejectedValueOnce(new Error('Network error'));

    // Mock do alert
    window.alert = vi.fn();

    render(<App />);
    
    const emailInput = screen.getByLabelText('Email');
    const passwordInput = screen.getByLabelText('Senha');
    const submitButton = screen.getByRole('button', { name: /entrar/i });
    
    fireEvent.change(emailInput, { target: { value: 'admin@beepy.com' } });
    fireEvent.change(passwordInput, { target: { value: 'admin123' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(window.alert).toHaveBeenCalledWith('Erro de conexão. Tente novamente mais tarde.');
    });
  });

  test('shows loading state during login', async () => {
    fetch.mockImplementationOnce(() => new Promise(resolve => setTimeout(resolve, 100)));

    render(<App />);
    
    const emailInput = screen.getByLabelText('Email');
    const passwordInput = screen.getByLabelText('Senha');
    const submitButton = screen.getByRole('button', { name: /entrar/i });
    
    fireEvent.change(emailInput, { target: { value: 'admin@beepy.com' } });
    fireEvent.change(passwordInput, { target: { value: 'admin123' } });
    fireEvent.click(submitButton);
    
    expect(screen.getByText('Entrando...')).toBeInTheDocument();
  });

  test('checks authentication on mount with valid token', async () => {
    localStorageMock.getItem.mockReturnValue('valid-token');
    
    const mockUserResponse = {
      user: {
        id: 1,
        name: 'Admin User',
        email: 'admin@beepy.com',
        role: 'admin'
      }
    };

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockUserResponse,
    });

    render(<App />);
    
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:10000/auth/verify',
        expect.objectContaining({
          method: 'GET',
          headers: {
            'Authorization': 'Bearer valid-token',
            'Content-Type': 'application/json'
          }
        })
      );
    });
  });

  test('removes invalid token on mount', async () => {
    localStorageMock.getItem.mockReturnValue('invalid-token');
    
    fetch.mockResolvedValueOnce({
      ok: false,
    });

    render(<App />);
    
    await waitFor(() => {
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('access_token');
    });
  });

  test('renders admin dashboard when authenticated as admin', async () => {
    const mockUserResponse = {
      user: {
        id: 1,
        name: 'Admin User',
        email: 'admin@beepy.com',
        role: 'admin'
      }
    };

    // Mock da verificação de token
    localStorageMock.getItem.mockReturnValue('valid-token');
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockUserResponse,
    });

    render(<App />);
    
    await waitFor(() => {
      expect(screen.getByText('Admin User')).toBeInTheDocument();
      expect(screen.getByText('Administrador')).toBeInTheDocument();
    });
  });

  test('renders ambassador dashboard when authenticated as ambassador', async () => {
    const mockUserResponse = {
      user: {
        id: 2,
        name: 'Ambassador User',
        email: 'ambassador@beepy.com',
        role: 'embaixadora'
      }
    };

    // Mock da verificação de token
    localStorageMock.getItem.mockReturnValue('valid-token');
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockUserResponse,
    });

    render(<App />);
    
    await waitFor(() => {
      expect(screen.getByText('Ambassador User')).toBeInTheDocument();
      expect(screen.getByText('Embaixadora')).toBeInTheDocument();
    });
  });

  test('handles logout', async () => {
    const mockUserResponse = {
      user: {
        id: 1,
        name: 'Admin User',
        email: 'admin@beepy.com',
        role: 'admin'
      }
    };

    // Mock da verificação de token
    localStorageMock.getItem.mockReturnValue('valid-token');
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockUserResponse,
    });

    render(<App />);
    
    await waitFor(() => {
      expect(screen.getByText('Admin User')).toBeInTheDocument();
    });

    const logoutButton = screen.getByRole('button', { name: /sair/i });
    fireEvent.click(logoutButton);
    
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('access_token');
    expect(screen.getByText('Sistema de Indicações e Comissões')).toBeInTheDocument();
  });
});

