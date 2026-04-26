import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="glass-card mx-4 mt-4 px-6 py-3 flex items-center justify-between animate-fade-in">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-500 to-purple-500 flex items-center justify-center">
          <span className="text-sm font-bold">P</span>
        </div>
        <Link to={user?.role === 'reviewer' ? '/reviewer' : '/'} className="text-lg font-semibold gradient-text">
          Playto KYC
        </Link>
      </div>

      <div className="flex items-center gap-4">
        <div className="hidden sm:flex items-center gap-2 text-sm text-gray-400">
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span>{user?.name}</span>
          <span className="px-2 py-0.5 rounded-md text-xs font-medium bg-brand-500/20 text-brand-300 border border-brand-500/30">
            {user?.role}
          </span>
        </div>
        <button
          onClick={handleLogout}
          id="logout-btn"
          className="text-sm text-gray-400 hover:text-white transition-colors duration-200"
        >
          Logout
        </button>
      </div>
    </nav>
  );
}
