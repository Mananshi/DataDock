# Use an official Node.js runtime as a base image
FROM node:18-alpine

# Set the working directory in the container
WORKDIR /app

# Copy the package.json and package-lock.json files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application files
COPY . .

# Expose the port that Next.js runs on
EXPOSE 3000

# Start Next.js in development mode
CMD ["npm", "run", "dev"]
