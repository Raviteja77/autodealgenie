"use client";

import { Suspense } from "react";
import { useState, useEffect, useRef } from "react";
import { useSearchParams, useRouter } from "next/navigation";
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
  Alert,
} from "@mui/material";
import {
  Send,
  SmartToy,
  Person,
  AttachMoney,
  DirectionsCar,
  Speed,
  LocalGasStation,
  Warning,
} from "@mui/icons-material";
import Header from "@/components/common/Header";
import Footer from "@/components/common/Footer";
import ProgressStepper from "@/components/common/ProgressStepper";
import Link from "next/link";
import { useStepper } from "@/app/context";

interface Message {
  id: number;
  text: string;
  sender: "user" | "ai";
  timestamp: Date;
}

interface VehicleInfo {
  vin?: string;
  make: string;
  model: string;
  year: number;
  price: number;
  mileage: number;
  fuelType: string;
}

function NegotiationContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { completeStep, setStepData, getStepData, canNavigateToStep, isStepCompleted } = useStepper();
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
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Check if user can access this step
  useEffect(() => {
    if (!canNavigateToStep(2)) {
      router.push("/dashboard/search");
    }
  }, [canNavigateToStep, router]);

  // Extract and validate vehicle data from URL params
  const vehicleData: VehicleInfo | null = (() => {
    try {
      const vin = searchParams.get("vin") || undefined;
      const make = searchParams.get("make");
      const model = searchParams.get("model");
      const yearStr = searchParams.get("year");
      const priceStr = searchParams.get("price");
      const mileageStr = searchParams.get("mileage");
      const fuelType = searchParams.get("fuelType");

      // Validate required fields
      if (!make || !model || !yearStr || !priceStr || !mileageStr) {
        return null;
      }

      const year = parseInt(yearStr);
      const price = parseFloat(priceStr);
      const mileage = parseInt(mileageStr);

      // Validate parsed values
      if (isNaN(year) || isNaN(price) || isNaN(mileage)) {
        return null;
      }

      return {
        vin,
        make,
        model,
        year,
        price,
        mileage,
        fuelType: fuelType || "Unknown",
      };
    } catch (err) {
      console.error("Error parsing vehicle data:", err);
      return null;
    }
  })();

  // Set error if vehicle data is invalid
  useEffect(() => {
    if (!vehicleData) {
      setError("Invalid vehicle data. Please select a vehicle from the search results.");
    }
  }, [vehicleData]);

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
    if (!vehicleData) return "Sorry, I don't have vehicle information to work with.";
    
    const input = userInput.toLowerCase();
    if (input.includes("price") || input.includes("cost")) {
      return `Based on market analysis, the fair market value for this ${vehicleData.year} ${vehicleData.make} ${vehicleData.model} is around $${vehicleData.price - 2000}. I recommend making an initial offer of $${vehicleData.price - 3000} to leave room for negotiation.`;
    } else if (input.includes("mileage")) {
      return `The vehicle has ${vehicleData.mileage.toLocaleString()} miles, which is ${vehicleData.mileage < 30000 ? "excellent" : "acceptable"} for a ${vehicleData.year} model. This is a positive factor in negotiation.`;
    } else if (input.includes("offer")) {
      return `I suggest starting with an offer of $${vehicleData.price - 3000}. Be prepared to go up to $${vehicleData.price - 1500} if needed. Would you like me to draft a negotiation script?`;
    }
    return "I can help you analyze the vehicle's price, market value, and create a negotiation strategy. What specific aspect would you like to discuss?";
  };

  const handleCompleteNegotiation = () => {
    // Mark negotiation step as completed
    completeStep(2, {
      messages: messages,
      vehicleData: vehicleData,
      timestamp: new Date().toISOString(),
    });
    // Navigate to evaluation page
    if (vehicleData) {
      const vehicleParams = new URLSearchParams({
        vin: vehicleData.vin || '',
        make: vehicleData.make,
        model: vehicleData.model,
        year: vehicleData.year.toString(),
        price: vehicleData.price.toString(),
        mileage: vehicleData.mileage.toString(),
        fuelType: vehicleData.fuelType || '',
      });
      router.push(`/dashboard/evaluation?${vehicleParams.toString()}`);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <Box sx={{ display: "flex", flexDirection: "column" }}>
      <Box sx={{ bgcolor: "background.default", flexGrow: 1 }}>
        <Container maxWidth="lg">

          {/* Error Alert */}
          {error && (
            <Alert severity="error" sx={{ mb: 3 }} icon={<Warning />}>
              <Typography variant="h6" gutterBottom>
                Unable to Load Vehicle Data
              </Typography>
              <Typography variant="body2" sx={{ mb: 2 }}>
                {error}
              </Typography>
              <Link href="/dashboard/results" style={{ textDecoration: "none" }}>
                <Button variant="contained" size="small">
                  Back to Results
                </Button>
              </Link>
            </Alert>
          )}

          {vehicleData && (
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
                      {vehicleData.year} {vehicleData.make} {vehicleData.model}
                    </Typography>
                  </Box>
                  {vehicleData.vin && (
                    <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                      <Typography variant="caption" color="text.secondary">
                        VIN: {vehicleData.vin}
                      </Typography>
                    </Box>
                  )}
                  <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                    <AttachMoney sx={{ mr: 1, color: "primary.main" }} />
                    <Typography variant="body1">
                      ${vehicleData.price.toLocaleString()}
                    </Typography>
                  </Box>
                  <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                    <Speed sx={{ mr: 1, color: "primary.main" }} />
                    <Typography variant="body1">
                      {vehicleData.mileage.toLocaleString()} miles
                    </Typography>
                  </Box>
                  <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                    <LocalGasStation sx={{ mr: 1, color: "primary.main" }} />
                    <Typography variant="body1">{vehicleData.fuelType}</Typography>
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
                  
                  {/* Complete Negotiation Button */}
                  <Box sx={{ mt: 2, display: "flex", justifyContent: "flex-end" }}>
                    <Button
                      variant="contained"
                      color="success"
                      onClick={handleCompleteNegotiation}
                      disabled={!vehicleData}
                    >
                      Complete Negotiation & Evaluate
                    </Button>
                  </Box>
                </Box>
              </Paper>
            </Grid>
          </Grid>
          )}
        </Container>
      </Box>
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
