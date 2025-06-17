import { Router, Request, Response } from 'express';
import bcrypt from 'bcryptjs';
import User from '../models/User';

const router = Router();

// Register endpoint
router.post('/register', async (req: Request, res: Response): Promise<void> => {
  try {
    console.log('Register request received:', req.body);
    const { username, password } = req.body;
    
    if (!username || !password) {
      console.log('Missing credentials:', { username: !!username, password: !!password });
      res.status(400).json({ 
        success: false,
        message: 'Username and password are required.' 
      });
      return;
    }

    const existingUser = await User.findOne({ username });
    if (existingUser) {
      console.log('User already exists:', username);
      res.status(409).json({ 
        success: false,
        message: 'Username already exists.' 
      });
      return;
    }

    const hashedPassword = await bcrypt.hash(password, 10);
    const user = new User({ 
      username, 
      password: hashedPassword 
    });
    
    await user.save();
    console.log('User registered successfully:', username);
    
    res.status(201).json({ 
      success: true,
      message: 'User registered successfully.' 
    });
  } catch (err) {
    console.error('Register error details:', err instanceof Error ? err.message : err);
    if (err instanceof Error && err.name === 'MongoServerError') {
      console.error('MongoDB Error:', err);
    }
    res.status(500).json({ 
      success: false,
      message: 'Server error during registration.',
      error: err instanceof Error ? err.message : 'Unknown error'
    });
  }
});

// Login endpoint
router.post('/login', async (req: Request, res: Response): Promise<void> => {
  try {
    console.log('Login request received:', { username: req.body.username });
    const { username, password } = req.body;

    if (!username || !password) {
      console.log('Missing credentials:', { username: !!username, password: !!password });
      res.status(400).json({ 
        success: false,
        message: 'Username and password are required.' 
      });
      return;
    }

    const user = await User.findOne({ username });
    if (!user) {
      console.log('User not found:', username);
      res.status(401).json({ 
        success: false,
        message: 'Invalid credentials.' 
      });
      return;
    }

    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) {
      console.log('Invalid password for user:', username);
      res.status(401).json({ 
        success: false,
        message: 'Invalid credentials.' 
      });
      return;
    }

    console.log('User logged in successfully:', username);
    res.status(200).json({ 
      success: true,
      message: 'Login successful.',
      userId: user._id 
    });
  } catch (err) {
    console.error('Login error details:', err instanceof Error ? err.message : err);
    if (err instanceof Error && err.name === 'MongoServerError') {
      console.error('MongoDB Error:', err);
    }
    res.status(500).json({ 
      success: false,
      message: 'Server error during login.',
      error: err instanceof Error ? err.message : 'Unknown error'
    });
  }
});

export default router;
