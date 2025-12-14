"use client";

import { Suspense } from "react";
import { useState, useEffect, useRef } from "react";
import { useSearchParams } from "next/navigation";
import {
  Box,
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Avatar,
  Card,
  CardContent,
  Grid,
  Divider,
} from "@mui/material";
import {
  Send,
  SmartToy,
  Person,
  AttachMoney,
  DirectionsCar,
  Speed,
  LocalGasStation,
} from "@mui/icons-material";
import Header from "@/components/common/Header";
import Footer from "@/components/common/Footer";
import ProgressStepper from "@/components/common/ProgressStepper";

interface Message {
  id: number;
  text: string;
  sender: "user" | "ai";
  timestamp: Date;
}

interface VehicleInfo {
  make: string;
  model: string;
  year: number;
  price: number;
  mileage: number;
  fuelType: string;
}

function NegotiationContent() {
  const searchParams = useSearchParams();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      text: "Hello! I'm your AI negotiation assistant. I'll help you get the best deal on this vehicle. What would you like to discuss?",
      sender: "ai",
      timestamp: new Date(),
    },
  ]);
  const [inputMessage, setInputMessage] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Mock vehicle data (in production, fetch from API based on vehicle ID)
  const vehicle: VehicleInfo = {
    make: searchParams.get("make") || "Toyota",
    model: searchParams.get("model") || "Camry",
    year: parseInt(searchParams.get("year") || "2022"),
    price: parseInt(searchParams.get("price") || "28500"),
    mileage: parseInt(searchParams.get("mileage") || "15000"),
    fuelType: searchParams.get("fuelType") || "Gasoline",
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage: Message = {
      id: messages.length + 1,
      text: inputMessage,
      sender: "user",
      timestamp: new Date(),
    };

    setMessages([...messages, userMessage]);
    setInputMessage("");
    setIsTyping(true);

    // Simulate AI response (in production, call your AI service)
    setTimeout(() => {
      const aiResponse: Message = {
        id: messages.length + 2,
        text: getAIResponse(inputMessage),
        sender: "ai",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiResponse]);
      setIsTyping(false);
    }, 1500);
  };

  const getAIResponse = (userInput: string): string => {
    const input = userInput.toLowerCase();
    if (input.includes("price") || input.includes("cost")) {
      return `Based on market analysis, the fair market value for this ${vehicle.year} ${vehicle.make} ${vehicle.model} is around $${vehicle.price - 2000}. I recommend making an initial offer of $${vehicle.price - 3000} to leave room for negotiation.`;
    } else if (input.includes("mileage")) {
      return `The vehicle has ${vehicle.mileage.toLocaleString()} miles, which is ${vehicle.mileage < 30000 ? "excellent" : "acceptable"} for a ${vehicle.year} model. This is a positive factor in negotiation.`;
    } else if (input.includes("offer")) {
      return `I suggest starting with an offer of $${vehicle.price - 3000}. Be prepared to go up to $${vehicle.price - 1500} if needed. Would you like me to draft a negotiation script?`;
    }
    return "I can help you analyze the vehicle's price, market value, and create a negotiation strategy. What specific aspect would you like to discuss?";
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <Box sx={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      <Header />
      <Box sx={{ pt: 10, pb: 4, bgcolor: "background.default", flexGrow: 1 }}>
        <Container maxWidth="lg">
          <ProgressStepper
            activeStep={2}
            steps={["Search", "Results", "Negotiate", "Evaluate", "Finalize"]}
          />

          <Grid container spacing={3}>
            {/* Vehicle Info Sidebar */}
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Vehicle Details
                  </Typography>
                  <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                    <DirectionsCar sx={{ mr: 1, color: "primary.main" }} />
                    <Typography variant="body1">
                      {vehicle.year} {vehicle.make} {vehicle.model}
                    </Typography>
                  </Box>
                  <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                    <AttachMoney sx={{ mr: 1, color: "primary.main" }} />
                    <Typography variant="body1">
                      ${vehicle.price.toLocaleString()}
                    </Typography>
                  </Box>
                  <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                    <Speed sx={{ mr: 1, color: "primary.main" }} />
                    <Typography variant="body1">
                      {vehicle.mileage.toLocaleString()} miles
                    </Typography>
                  </Box>
                  <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                    <LocalGasStation sx={{ mr: 1, color: "primary.main" }} />
                    <Typography variant="body1">{vehicle.fuelType}</Typography>
                  </Box>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="subtitle2" gutterBottom>
                    Negotiation Tips
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    • Research market value before making an offer
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    • Be polite but firm in your negotiations
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    • Don&apos;t be afraid to walk away
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            {/* Chat Area */}
            <Grid item xs={12} md={8}>
              <Paper
                elevation={2}
                sx={{
                  height: "600px",
                  display: "flex",
                  flexDirection: "column",
                }}
              >
                {/* Messages Area */}
                <Box
                  sx={{
                    flexGrow: 1,
                    overflow: "auto",
                    p: 3,
                    display: "flex",
                    flexDirection: "column",
                    gap: 2,
                  }}
                >
                  {messages.map((message) => (
                    <Box
                      key={message.id}
                      sx={{
                        display: "flex",
                        justifyContent:
                          message.sender === "user" ? "flex-end" : "flex-start",
                        gap: 1,
                      }}
                    >
                      {message.sender === "ai" && (
                        <Avatar
                          sx={{
                            bgcolor: "primary.main",
                            width: 36,
                            height: 36,
                          }}
                        >
                          <SmartToy fontSize="small" />
                        </Avatar>
                      )}
                      <Paper
                        elevation={1}
                        sx={{
                          p: 2,
                          maxWidth: "70%",
                          bgcolor:
                            message.sender === "user"
                              ? "primary.main"
                              : "background.paper",
                          color:
                            message.sender === "user"
                              ? "primary.contrastText"
                              : "text.primary",
                        }}
                      >
                        <Typography variant="body1">{message.text}</Typography>
                        <Typography
                          variant="caption"
                          sx={{
                            display: "block",
                            mt: 0.5,
                            opacity: 0.7,
                          }}
                        >
                          {message.timestamp.toLocaleTimeString([], {
                            hour: "2-digit",
                            minute: "2-digit",
                          })}
                        </Typography>
                      </Paper>
                      {message.sender === "user" && (
                        <Avatar
                          sx={{
                            bgcolor: "secondary.main",
                            width: 36,
                            height: 36,
                          }}
                        >
                          <Person fontSize="small" />
                        </Avatar>
                      )}
                    </Box>
                  ))}
                  {isTyping && (
                    <Box sx={{ display: "flex", gap: 1 }}>
                      <Avatar
                        sx={{ bgcolor: "primary.main", width: 36, height: 36 }}
                      >
                        <SmartToy fontSize="small" />
                      </Avatar>
                      <Paper elevation={1} sx={{ p: 2 }}>
                        <Typography variant="body2">Typing...</Typography>
                      </Paper>
                    </Box>
                  )}
                  <div ref={messagesEndRef} />
                </Box>

                {/* Input Area */}
                <Box
                  sx={{
                    p: 2,
                    borderTop: "1px solid",
                    borderColor: "divider",
                  }}
                >
                  <Box sx={{ display: "flex", gap: 1 }}>
                    <TextField
                      fullWidth
                      multiline
                      maxRows={3}
                      placeholder="Type your message..."
                      value={inputMessage}
                      onChange={(e) => setInputMessage(e.target.value)}
                      onKeyPress={handleKeyPress}
                      variant="outlined"
                      size="small"
                    />
                    <Button
                      variant="contained"
                      endIcon={<Send />}
                      onClick={handleSendMessage}
                      disabled={!inputMessage.trim() || isTyping}
                    >
                      Send
                    </Button>
                  </Box>
                </Box>
              </Paper>
            </Grid>
          </Grid>
        </Container>
      </Box>
      <Footer />
    </Box>
  );
}

export default function NegotiationPage() {
  return (
    <Suspense fallback={
      <Box sx={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "100vh" }}>
        <Typography>Loading...</Typography>
      </Box>
    }>
      <NegotiationContent />
    </Suspense>
  );
}
