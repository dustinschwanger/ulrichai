import React from 'react';
import { Plus, MessageSquare } from 'lucide-react';
import './Sidebar.css';

interface Chat {
  id: string;
  title: string;
  timestamp: Date;
}

interface SidebarProps {
  currentChatId: string;
  chats: Chat[];
  onNewChat: () => void;
  onSelectChat: (chatId: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ 
  currentChatId, 
  chats, 
  onNewChat, 
  onSelectChat 
}) => {
  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h1>Ulrich AI</h1>
        <button className="new-chat-button" onClick={onNewChat}>
          <Plus size={18} />
          New chat
        </button>
      </div>
      
      <div className="chat-history">
        {chats.length === 0 ? (
          <div className="empty-history">
            <MessageSquare size={24} style={{ opacity: 0.3 }} />
            <p>No conversations yet</p>
          </div>
        ) : (
          <div className="chat-list">
            {chats.map((chat) => (
              <div
                key={chat.id}
                className={`chat-item ${currentChatId === chat.id ? 'active' : ''}`}
                onClick={() => onSelectChat(chat.id)}
              >
                <MessageSquare size={16} />
                <div className="chat-item-content">
                  <div className="chat-item-title">{chat.title}</div>
                  <div className="chat-item-date">
                    {new Date(chat.timestamp).toLocaleDateString()}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
      
      <div className="sidebar-footer">
        <div className="footer-content">
          <p>© 2024 The RBL Group</p>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;