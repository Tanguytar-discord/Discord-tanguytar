import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import io from 'socket.io-client';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ChatPage = ({ user, onLogout }) => {
  const [channels, setChannels] = useState([]);
  const [currentChannel, setCurrentChannel] = useState('general');
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [onlineUsers, setOnlineUsers] = useState([]);
  const [socket, setSocket] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    fetchChannels();
    fetchMessages();
    fetchOnlineUsers();
    initializeSocket();

    return () => {
      if (socket) {
        socket.disconnect();
      }
    };
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const initializeSocket = () => {
    const token = localStorage.getItem('auth_token');
    const newSocket = io(BACKEND_URL, {
      auth: { token },
      path: '/ws/' + user.id
    });

    newSocket.on('connect', () => {
      console.log('Connected to WebSocket');
    });

    newSocket.on('new_message', (data) => {
      const messageData = JSON.parse(data);
      if (messageData.type === 'new_message') {
        setMessages(prev => [...prev, messageData.data]);
      }
    });

    setSocket(newSocket);
  };

  const fetchChannels = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await axios.get(`${API}/channels`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setChannels(response.data);
    } catch (error) {
      console.error('Erreur lors du chargement des canaux:', error);
      toast.error('Erreur lors du chargement des canaux');
    }
  };

  const fetchMessages = async (channelId = 'general') => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await axios.get(`${API}/channels/${channelId}/messages`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setMessages(response.data);
    } catch (error) {
      console.error('Erreur lors du chargement des messages:', error);
    }
  };

  const fetchOnlineUsers = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await axios.get(`${API}/users/online`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setOnlineUsers(response.data);
    } catch (error) {
      console.error('Erreur lors du chargement des utilisateurs en ligne:', error);
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim()) return;

    try {
      const token = localStorage.getItem('auth_token');
      await axios.post(`${API}/channels/${currentChannel}/messages`, 
        { content: newMessage },
        { headers: { 'Authorization': `Bearer ${token}` } }
      );
      setNewMessage('');
    } catch (error) {
      console.error('Erreur lors de l\'envoi du message:', error);
      toast.error('Erreur lors de l\'envoi du message');
    }
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('fr-FR', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="h-screen bg-gray-900 text-white flex">
      {/* Sidebar des canaux */}
      <div className="w-64 bg-gray-800 flex flex-col">
        <div className="p-4 border-b border-gray-700">
          <h1 className="text-xl font-bold text-white">ConvoTalk</h1>
        </div>
        
        <div className="flex-1 p-4">
          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-2">
            Canaux textuels
          </h3>
          <div className="space-y-1">
            <button
              onClick={() => {
                setCurrentChannel('general');
                fetchMessages('general');
              }}
              className={`w-full text-left px-2 py-1 rounded hover:bg-gray-700 transition-colors ${
                currentChannel === 'general' ? 'bg-gray-700' : ''
              }`}
            >
              # général
            </button>
            {channels.map((channel) => (
              <button
                key={channel.id}
                onClick={() => {
                  setCurrentChannel(channel.id);
                  fetchMessages(channel.id);
                }}
                className={`w-full text-left px-2 py-1 rounded hover:bg-gray-700 transition-colors ${
                  currentChannel === channel.id ? 'bg-gray-700' : ''
                }`}
              >
                # {channel.name}
              </button>
            ))}
          </div>
        </div>

        {/* Profil utilisateur */}
        <div className="p-4 border-t border-gray-700 flex items-center justify-between">
          <div className="flex items-center">
            <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
              {user.username[0].toUpperCase()}
            </div>
            <span className="ml-2 text-sm">{user.username}</span>
          </div>
          <button
            onClick={onLogout}
            className="text-gray-400 hover:text-white transition-colors"
            title="Déconnexion"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
          </button>
        </div>
      </div>

      {/* Zone de chat principale */}
      <div className="flex-1 flex flex-col">
        {/* En-tête du canal */}
        <div className="p-4 border-b border-gray-700 bg-gray-800">
          <h2 className="text-xl font-semibold">
            # {currentChannel === 'general' ? 'général' : channels.find(c => c.id === currentChannel)?.name || 'Canal'}
          </h2>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message) => (
            <div key={message.id} className="flex items-start space-x-3">
              <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0">
                {message.sender_username[0].toUpperCase()}
              </div>
              <div className="flex-1">
                <div className="flex items-center space-x-2">
                  <span className="font-semibold text-white">{message.sender_username}</span>
                  <span className="text-xs text-gray-400">{formatTime(message.timestamp)}</span>
                </div>
                <p className="text-gray-300 mt-1">{message.content}</p>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Zone de saisie */}
        <div className="p-4 border-t border-gray-700 bg-gray-800">
          <form onSubmit={sendMessage} className="flex space-x-2">
            <input
              type="text"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              placeholder={`Envoyer un message dans #${currentChannel === 'general' ? 'général' : channels.find(c => c.id === currentChannel)?.name || 'canal'}`}
              className="flex-1 bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              type="submit"
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition-colors"
            >
              Envoyer
            </button>
          </form>
        </div>
      </div>

      {/* Sidebar utilisateurs en ligne */}
      <div className="w-64 bg-gray-800 border-l border-gray-700">
        <div className="p-4">
          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-4">
            En ligne — {onlineUsers.length}
          </h3>
          <div className="space-y-2">
            {onlineUsers.map((onlineUser) => (
              <div key={onlineUser.id} className="flex items-center space-x-3">
                <div className="relative">
                  <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                    {onlineUser.username[0].toUpperCase()}
                  </div>
                  <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-green-400 rounded-full border-2 border-gray-800"></div>
                </div>
                <span className="text-sm text-gray-300">{onlineUser.username}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;