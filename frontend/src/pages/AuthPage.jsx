import React, { useState, useMemo, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { LogIn, UserPlus, ArrowRight, ShieldCheck, Mail, Phone, Lock, Hash, MapPin, AlertCircle, Eye, EyeOff, Loader2 } from 'lucide-react';
import { apiService } from '../services/api';
import { useAuth } from '../context/AuthContext';
import ThemeToggle from '../components/shared/ThemeToggle';

const AuthPage = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const { login, isAuthenticated, isLoading: authLoading } = useAuth();
    
    const [isLogin, setIsLogin] = useState(true);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);
    const [showPassword, setShowPassword] = useState(false);

    const [form, setForm] = useState({
        first_name: '',
        middle_name: '',
        last_name: '',
        pan_number: '',
        aadhar_number: '',
        aadhar_pincode: '',
        mobile_number: '',
        email: '',
        password: ''
    });

    // Auto-redirect if already authenticated
    useEffect(() => {
        if (!authLoading && isAuthenticated) {
            const destination = location.state?.from?.pathname || '/itr-select';
            navigate(destination, { replace: true });
        }
    }, [isAuthenticated, authLoading, navigate, location]);

    // Validation Logic
    const validations = useMemo(() => {
        const panRegex = /^[A-Z]{5}[0-9]{4}[A-Z]$/;
        const aadharRegex = /^[0-9]{12}$/;
        const mobileRegex = /^[0-9]{10}$/;
        const pincodeRegex = /^[0-9]{6}$/;
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        return {
            pan: panRegex.test(form.pan_number.toUpperCase()),
            aadhar: aadharRegex.test(form.aadhar_number.replace(/\s/g, '')),
            mobile: mobileRegex.test(form.mobile_number),
            pincode: pincodeRegex.test(form.aadhar_pincode),
            email: emailRegex.test(form.email),
            password: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{12,}$/.test(form.password),
            first_name: form.first_name.trim().length > 0,
            last_name: form.last_name.trim().length > 0
        };
    }, [form]);

    const isFormValid = isLogin
        ? (validations.pan && validations.password)
        : (validations.first_name && validations.last_name && validations.pan &&
            validations.aadhar && validations.pincode && validations.mobile &&
            validations.email && validations.password);

    const handleChange = (e) => {
        let value = e.target.value;
        if (e.target.name === 'pan_number') value = value.toUpperCase();
        setForm({ ...form, [e.target.name]: value });
        if (error) setError(null);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!isFormValid) return;

        setLoading(true);
        setError(null);

        try {
            if (isLogin) {
                const data = await login(form.pan_number, form.password);
                setSuccess(`Welcome back, ${data.user.first_name}!`);
            } else {
                await apiService.signup({
                    ...form,
                    aadhar_number: form.aadhar_number.replace(/\s/g, '')
                });
                setSuccess(`Account created! You can now log in.`);
                setIsLogin(true); // Switch to login after signup
            }
        } catch (err) {
            setError(err.message || "An unexpected error occurred");
        } finally {
            setLoading(false);
        }
    };

    if (authLoading) {
        return (
            <div className="flex items-center justify-center min-h-screen bg-[#0a0a0a]">
                <Loader2 className="w-12 h-12 text-primary animate-spin" />
            </div>
        );
    }

    if (success && isLogin) {
        return (
            <div className="auth-container">
                <div className="glass-card" style={{ textAlign: 'center' }}>
                    <div style={{ background: 'var(--success)', width: '64px', height: '64px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1.5rem' }}>
                        <ShieldCheck size={32} color="#fff" />
                    </div>
                    <h1>Authenticated</h1>
                    <p className="subtitle">{success}</p>
                    <button className="btn btn-primary" onClick={() => navigate('/itr-select')}>
                        Continue to Filing <ArrowRight size={18} />
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="auth-container">
            <div style={{ position: 'absolute', top: '2rem', right: '2rem' }}>
                <ThemeToggle />
            </div>
            <div className="glass-card">
                <header style={{ marginBottom: '3.5rem' }}>
                    <h1 style={{ marginBottom: '1rem' }}>{isLogin ? 'Sign In' : 'Create Account'}</h1>
                    <p className="subtitle" style={{ fontSize: '1rem', lineHeight: '1.6' }}>
                        {isLogin ? 'Secure access to your professional tax filing dashboard.' : 'Initialize your professional-grade tax filing profile.'}
                    </p>
                </header>

                <form onSubmit={handleSubmit}>
                    {!isLogin && (
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem' }}>
                            <div className="input-group">
                                <label className="input-label">First Name</label>
                                <input type="text" name="first_name" className="input-field" placeholder="John" required value={form.first_name} onChange={handleChange} />
                                {form.first_name && !validations.first_name && <span className="error-text">Required</span>}
                            </div>
                            <div className="input-group">
                                <label className="input-label">Middle Name</label>
                                <input type="text" name="middle_name" className="input-field" placeholder="Paul" value={form.middle_name} onChange={handleChange} />
                            </div>
                            <div className="input-group">
                                <label className="input-label">Last Name</label>
                                <input type="text" name="last_name" className="input-field" placeholder="Doe" required value={form.last_name} onChange={handleChange} />
                                {form.last_name && !validations.last_name && <span className="error-text">Required</span>}
                            </div>
                        </div>
                    )}

                    <div className="input-group">
                        <label className="input-label">PAN Number</label>
                        <div style={{ position: 'relative' }}>
                            <Hash size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                            <input type="text" name="pan_number" className="input-field tabular-nums" style={{ paddingLeft: '3rem', borderColor: form.pan_number && !validations.pan ? 'var(--error)' : '' }} placeholder="ABCDE1234F" required value={form.pan_number} onChange={handleChange} maxLength={10} />
                        </div>
                        {form.pan_number && !validations.pan && <span className="error-text">Invalid PAN format</span>}
                    </div>

                    {!isLogin && (
                        <>
                            <div className="input-group">
                                <label className="input-label">Aadhar Number</label>
                                <div style={{ position: 'relative' }}>
                                    <ShieldCheck size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                                    <input type="text" name="aadhar_number" className="input-field tabular-nums" style={{ paddingLeft: '3rem', borderColor: form.aadhar_number && !validations.aadhar ? 'var(--error)' : '' }} placeholder="1234 5678 9012" required value={form.aadhar_number} onChange={handleChange} maxLength={14} />
                                </div>
                                {form.aadhar_number && !validations.aadhar && <span className="error-text">Invalid Aadhar</span>}
                            </div>
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
                                <div className="input-group">
                                    <label className="input-label">Pincode</label>
                                    <input type="text" name="aadhar_pincode" className="input-field tabular-nums" style={{ borderColor: form.aadhar_pincode && !validations.pincode ? 'var(--error)' : '' }} placeholder="400001" required value={form.aadhar_pincode} onChange={handleChange} maxLength={6} />
                                    {form.aadhar_pincode && !validations.pincode && <span className="error-text">6 digits</span>}
                                </div>
                                <div className="input-group">
                                    <label className="input-label">Email</label>
                                    <input type="email" name="email" className="input-field" style={{ borderColor: form.email && !validations.email ? 'var(--error)' : '' }} placeholder="john@example.com" required value={form.email} onChange={handleChange} />
                                    {form.email && !validations.email && <span className="error-text">Invalid email</span>}
                                </div>
                            </div>

                            <div className="input-group">
                                <label className="input-label">Mobile Number</label>
                                <div style={{ position: 'relative' }}>
                                    <Phone size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                                    <input type="text" name="mobile_number" className="input-field tabular-nums" style={{ paddingLeft: '3rem', borderColor: form.mobile_number && !validations.mobile ? 'var(--error)' : '' }} placeholder="9876543210" required value={form.mobile_number} onChange={handleChange} maxLength={10} />
                                </div>
                                {form.mobile_number && !validations.mobile && <span className="error-text">10 digits</span>}
                            </div>
                        </>
                    )}

                    <div className="input-group">
                        <label className="input-label">Password</label>
                        <div style={{ position: 'relative' }}>
                            <Lock size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-secondary)' }} />
                            <input type={showPassword ? "text" : "password"} name="password" className="input-field" style={{ paddingLeft: '3rem', paddingRight: '3rem', borderColor: form.password && !validations.password ? 'var(--error)' : '' }} placeholder="••••••••" required value={form.password} onChange={handleChange} />
                            <div onClick={() => setShowPassword(!showPassword)} style={{ position: 'absolute', right: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-secondary)', cursor: 'pointer' }}>
                                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                            </div>
                        </div>
                        {!isLogin && (
                            <div style={{ marginTop: '0.75rem', padding: '0.75rem', background: 'rgba(255, 255, 255, 0.02)', borderRadius: '8px' }}>
                                <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.5rem', fontWeight: 600 }}>Password Requirements:</div>
                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
                                    <div style={{ fontSize: '0.7rem', display: 'flex', alignItems: 'center', gap: '0.35rem', color: form.password.length >= 12 ? 'var(--success)' : 'rgba(255, 255, 255, 0.3)' }}>
                                        <div style={{ width: '4px', height: '4px', borderRadius: '50%', background: 'currentColor' }}></div>
                                        12+ Characters
                                    </div>
                                    <div style={{ fontSize: '0.7rem', display: 'flex', alignItems: 'center', gap: '0.35rem', color: /[A-Z]/.test(form.password) ? 'var(--success)' : 'rgba(255, 255, 255, 0.3)' }}>
                                        <div style={{ width: '4px', height: '4px', borderRadius: '50%', background: 'currentColor' }}></div>
                                        Uppercase
                                    </div>
                                    <div style={{ fontSize: '0.7rem', display: 'flex', alignItems: 'center', gap: '0.35rem', color: /[a-z]/.test(form.password) ? 'var(--success)' : 'rgba(255, 255, 255, 0.3)' }}>
                                        <div style={{ width: '4px', height: '4px', borderRadius: '50%', background: 'currentColor' }}></div>
                                        Lowercase
                                    </div>
                                    <div style={{ fontSize: '0.7rem', display: 'flex', alignItems: 'center', gap: '0.35rem', color: /\d/.test(form.password) ? 'var(--success)' : 'rgba(255, 255, 255, 0.3)' }}>
                                        <div style={{ width: '4px', height: '4px', borderRadius: '50%', background: 'currentColor' }}></div>
                                        Numbers
                                    </div>
                                    <div style={{ fontSize: '0.7rem', display: 'flex', alignItems: 'center', gap: '0.35rem', color: /[@$!%*?&]/.test(form.password) ? 'var(--success)' : 'rgba(255, 255, 255, 0.3)' }}>
                                        <div style={{ width: '4px', height: '4px', borderRadius: '50%', background: 'currentColor' }}></div>
                                        Special (@$!%*?&)
                                    </div>
                                </div>
                            </div>
                        )}
                        {form.password && !isLogin && !validations.password && <span className="error-text">Please meet all requirements</span>}
                    </div>

                    {error && (
                        <div className="error-text" style={{ marginBottom: '2rem', textAlign: 'left', display: 'flex', alignItems: 'center', gap: '0.75rem', color: 'var(--error)', background: 'var(--accent-soft)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--error)', fontSize: '0.875rem' }}>
                            <AlertCircle size={18} /> {error}
                        </div>
                    )}

                    {success && !isLogin && (
                         <div className="success-text" style={{ marginBottom: '2rem', textAlign: 'left', color: 'var(--success)', background: 'var(--accent-soft)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--success)', fontSize: '0.875rem' }}>
                            {success}
                         </div>
                    )}

                    <button className="btn btn-primary" type="submit" disabled={loading || !isFormValid}>
                        {loading ? <Loader2 className="animate-spin" size={18} /> : (isLogin ? 'Login Now' : 'Create Account')}
                        {!loading && (isLogin ? <LogIn size={18} /> : <UserPlus size={18} />)}
                    </button>
                </form>

                <div className="auth-toggle">
                    {isLogin ? "Don't have an account? " : "Already have an account? "}
                    <b onClick={() => { setIsLogin(!isLogin); setError(null); setSuccess(null); }}>{isLogin ? 'Sign Up' : 'Log In'}</b>
                </div>
            </div>
        </div>
    );
};

export default AuthPage;
