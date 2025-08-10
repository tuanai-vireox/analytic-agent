// MongoDB initialization script for LibreChat
// This script sets up the initial database structure

db = db.getSiblingDB('librechat');

// Create collections
db.createCollection('users');
db.createCollection('conversations');
db.createCollection('messages');
db.createCollection('files');
db.createCollection('analytics');

// Create indexes for better performance
db.users.createIndex({ "email": 1 }, { unique: true });
db.users.createIndex({ "username": 1 }, { unique: true });
db.conversations.createIndex({ "user": 1 });
db.conversations.createIndex({ "createdAt": -1 });
db.messages.createIndex({ "conversationId": 1 });
db.messages.createIndex({ "createdAt": -1 });
db.files.createIndex({ "user": 1 });
db.files.createIndex({ "createdAt": -1 });

// Insert default admin user (optional)
db.users.insertOne({
  email: "admin@analytic-agent.com",
  username: "admin",
  password: "$2b$10$rQZ8iJ8kL9mN0oP1qR2sT3uV4wX5yZ6aA7bB8cC9dD0eE1fF2gG3hH4iI5jJ6kK7lL8mM9nN0oO1pP2qQ3rR4sS5tT6uU7vV8wW9xX0yY1zZ",
  name: "System Administrator",
  avatar: null,
  role: "ADMIN",
  createdAt: new Date(),
  updatedAt: new Date()
});

print("MongoDB initialization completed successfully!"); 