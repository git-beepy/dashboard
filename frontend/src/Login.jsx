import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { BarChart3, Mail, User, UserCheck, Lock } from 'lucide-react';

const Login = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [password, setPassword] = useState('');
  const [userType, setUserType] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const { login, register } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      let result;
      if (isLogin) {
        if (!email || !password) {
          setError('Email e senha são obrigatórios');
          setLoading(false);
          return;
        }
        result = await login(email, password);
      } else {
        if (!email || !name || !userType || !password) {
          setError('Todos os campos são obrigatórios');
          setLoading(false);
          return;
        }
        result = await register({ email, name, user_type: userType, password });
      }

      if (!result.success) {
        setError(result.error);
      }
    } catch (error) {
      setError('Erro inesperado. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-screen bg-gradient-to-br from-yellow-50 to-orange-50 flex items-center justify-center p-1">
      <div className="w-full max-w-xs">
        <Card className="w-full shadow-sm">
          <CardHeader className="text-center pb-0.5 px-2 pt-1">
            <div className="flex justify-center mb-0.5">
              <div className="w-4 h-4 bg-yellow-400 rounded-md flex items-center justify-center">
                <BarChart3 className="w-2 h-2 text-gray-900" />
              </div>
            </div>
            <CardTitle className="text-xs font-bold">beepy</CardTitle>
            <CardDescription className="text-xs">
              Sistema de Indicações e Comissões
            </CardDescription>
          </CardHeader>

          <CardContent className="pt-0 px-2 pb-1">
            <div className="text-center mb-0.5">
              <h2 className="text-xs font-semibold">Bem-vindo de volta</h2>
              <p className="text-xs text-gray-600">
                Faça login para acessar sua conta
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-1">
              <div className="space-y-0">
                <Label htmlFor="email" className="text-xs">
                  Email
                </Label>
                <div className="relative">
                  <Mail className="absolute left-1.5 top-1 h-3 w-3 text-gray-400" />
                  <Input
                    id="email"
                    type="email"
                    placeholder="seu@email.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="pl-6 h-5 text-xs"
                    required
                    autoComplete="off"
                  />
                </div>
              </div>

              <div className="space-y-0">
                <Label htmlFor="password" className="text-xs">
                  Senha
                </Label>
                <div className="relative">
                  <Lock className="absolute left-1.5 top-1 h-3 w-3 text-gray-400" />
                  <Input
                    id="password"
                    type="password"
                    placeholder="Sua senha"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="pl-6 h-5 text-xs"
                    required
                    autoComplete="new-password"
                  />
                </div>
              </div>

              {!isLogin && (
                <>
                  <div className="space-y-0">
                    <Label htmlFor="name" className="text-xs">
                      Nome
                    </Label>
                    <div className="relative">
                      <User className="absolute left-1.5 top-1 h-3 w-3 text-gray-400" />
                      <Input
                        id="name"
                        type="text"
                        placeholder="Seu nome completo"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        className="pl-6 h-5 text-xs"
                        required
                      />
                    </div>
                  </div>

                  <div className="space-y-0">
                    <Label htmlFor="userType" className="text-xs">
                      Tipo de usuário
                    </Label>
                    <div className="relative">
                      <UserCheck className="absolute left-1.5 top-1 h-3 w-3 text-gray-400 z-10" />
                      <Select value={userType} onValueChange={setUserType} required>
                        <SelectTrigger className="pl-6 h-5 text-xs">
                          <SelectValue placeholder="Selecione o tipo" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="embaixadora">Embaixadora</SelectItem>
                          <SelectItem value="admin">Administrador</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                </>
              )}

              {error && (
                <div className="text-red-600 text-xs bg-red-50 p-1 rounded-md">
                  {error}
                </div>
              )}

              <Button
                type="submit"
                className="w-full bg-yellow-400 hover:bg-yellow-500 text-gray-900 h-5 text-xs"
                disabled={loading}
              >
                {loading ? 'Carregando...' : isLogin ? 'Entrar' : 'Criar conta'}
              </Button>
            </form>

            <div className="mt-1 text-center">
              <button
                type="button"
                onClick={() => {
                  setIsLogin(!isLogin);
                  setError('');
                  setEmail('');
                  setPassword('');
                  setName('');
                  setUserType('');
                }}
                className="text-xs text-gray-600 hover:text-gray-900"
              >
                {isLogin
                  ? 'Não tem uma conta? Criar conta'
                  : 'Já tem uma conta? Entrar'}
              </button>
            </div>
          </CardContent>
        </Card>

        <div className="mt-0.5 text-center">
          <p className="text-xs text-gray-500">
            © 2025 Beepy. Todos os direitos reservados.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
