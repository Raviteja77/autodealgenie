"use client";

import { useEffect } from "react";
import Link from "next/link";
import { apiClient, Deal } from "@/lib/api";
import { Button, Card, Spinner } from "@/components";
import { getUserFriendlyErrorMessage } from "@/lib/errors";
import { useApi } from "@/lib/hooks";
import Box from "@mui/material/Box";
import Container from "@mui/material/Container";
import Typography from "@mui/material/Typography";
import Chip from "@mui/material/Chip";
import ErrorOutlineIcon from "@mui/icons-material/ErrorOutline";
import Grid from "@mui/material/Grid";
import { useRouter } from "next/navigation";

// Constants for fallback values when data is unavailable
const DEFAULT_FUEL_TYPE = "Unknown";
const DEFAULT_CONDITION = "good";

export default function DealsPage() {
  const router = useRouter();
  const { data: deals, isLoading, error, execute } = useApi<Deal[]>();

  useEffect(() => {
    execute(() => apiClient.getDeals());
  }, [execute]);

  const getStatusColor = (status: string): "warning" | "info" | "success" | "error" | "default" => {
    switch (status) {
      case "pending":
        return "warning";
      case "in_progress":
        return "info";
      case "completed":
        return "success";
      case "cancelled":
        return "error";
      default:
        return "default";
    }
  };

  const getNavigationHint = (status: string): string | null => {
    switch (status) {
      case "in_progress":
        return "Click to continue negotiation";
      case "completed":
        return "Click to view deal evaluation";
      default:
        return null;
    }
  };

  const handleDealClick = (deal: Deal) => {
    // Use offer_price if available (negotiated price), otherwise asking_price
    const finalPrice = deal.offer_price || deal.asking_price;
    
    const vehicleParams = new URLSearchParams({
      make: deal.vehicle_make,
      model: deal.vehicle_model,
      year: deal.vehicle_year.toString(),
      price: finalPrice.toString(),
      mileage: deal.vehicle_mileage.toString(),
    });
    
    // Add VIN if available
    if (deal.vehicle_vin) {
      vehicleParams.set("vin", deal.vehicle_vin);
    }
    
    // Add fuelType with fallback
    vehicleParams.set("fuelType", DEFAULT_FUEL_TYPE);
    
    // Navigate based on deal status
    if (deal.status === "in_progress") {
      // In progress deals go to negotiation page
      router.push(`/dashboard/negotiation?${vehicleParams.toString()}`);
    } else if (deal.status === "completed") {
      // Completed deals go to evaluation page
      vehicleParams.set("condition", DEFAULT_CONDITION); // Add default condition for evaluation
      router.push(`/dashboard/evaluation?${vehicleParams.toString()}`);
    }
  };

  if (isLoading) {
    return (
      <Box
        sx={{
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          bgcolor: "background.default",
        }}
      >
        <Spinner size="lg" text="Loading deals..." />
      </Box>
    );
  }

  if (error) {
    return (
      <Box
        sx={{
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          bgcolor: "background.default",
          p: 2,
        }}
      >
        <Card padding="lg" shadow="lg" sx={{ maxWidth: 500, width: "100%" }}>
          <Card.Body>
            <Box sx={{ textAlign: "center" }}>
              <Box
                sx={{
                  width: 48,
                  height: 48,
                  bgcolor: "error.light",
                  borderRadius: "50%",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  mx: "auto",
                  mb: 2,
                }}
              >
                <ErrorOutlineIcon color="error" />
              </Box>
              <Typography variant="h5" gutterBottom fontWeight={600}>
                Error Loading Deals
              </Typography>
              <Typography color="error" sx={{ mb: 2 }}>
                {getUserFriendlyErrorMessage(error)}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Make sure the backend API is running at{" "}
                {process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}
              </Typography>
              <Box sx={{ display: "flex", gap: 1, justifyContent: "center" }}>
                <Link href="/" style={{ textDecoration: "none" }}>
                  <Button variant="outline">Go Home</Button>
                </Link>
                <Button onClick={() => execute(() => apiClient.getDeals())}>
                  Retry
                </Button>
              </Box>
            </Box>
          </Card.Body>
        </Card>
      </Box>
    );
  }

  return (
    <Box sx={{ minHeight: "100vh", bgcolor: "background.default", py: 4 }}>
      <Container maxWidth="lg">
        <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 4 }}>
          <Box>
            <Typography variant="h3" gutterBottom fontWeight={700}>
              Deals
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Manage your automotive deals
            </Typography>
          </Box>
          <Box sx={{ display: "flex", gap: 2 }}>
            <Link href="/" style={{ textDecoration: "none" }}>
              <Button variant="secondary">Home</Button>
            </Link>
            <Button variant="success" onClick={() => execute(() => apiClient.getDeals())}>
              Refresh
            </Button>
          </Box>
        </Box>

        {!deals || deals.length === 0 ? (
          <Card padding="lg" shadow="md">
            <Card.Body>
              <Box sx={{ textAlign: "center", py: 4 }}>
                <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
                  No deals found. The backend is connected but no deals have been created yet.
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  You can create deals using the API at{" "}
                  {process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/docs
                </Typography>
              </Box>
            </Card.Body>
          </Card>
        ) : (
          <Grid container spacing={3}>
            {deals.map((deal) => {
              const isClickable = deal.status === "in_progress" || deal.status === "completed";
              return (
                <Grid item xs={12} key={deal.id}>
                  <Card 
                    hover={isClickable} 
                    shadow="md" 
                    sx={{ cursor: isClickable ? "pointer" : "default" }} 
                    onClick={isClickable ? () => handleDealClick(deal) : undefined}
                  >
                  <Card.Body>
                    <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", mb: 2 }}>
                      <Box>
                        <Typography variant="h5" gutterBottom fontWeight={600}>
                          {deal.vehicle_year} {deal.vehicle_make} {deal.vehicle_model}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {deal.customer_name} ({deal.customer_email})
                        </Typography>
                      </Box>
                      <Chip
                        label={deal.status.replace("_", " ").toUpperCase()}
                        color={getStatusColor(deal.status)}
                        size="small"
                      />
                    </Box>
                    <Grid container spacing={2} sx={{ mb: 2 }}>
                      <Grid item xs={12} md={4}>
                        <Typography variant="caption" color="text.secondary">
                          Mileage:
                        </Typography>
                        <Typography variant="body2" fontWeight={600}>
                          {deal.vehicle_mileage.toLocaleString()} miles
                        </Typography>
                      </Grid>
                      <Grid item xs={12} md={4}>
                        <Typography variant="caption" color="text.secondary">
                          Asking Price:
                        </Typography>
                        <Typography variant="body2" fontWeight={600}>
                          ${deal.asking_price.toLocaleString()}
                        </Typography>
                      </Grid>
                      {deal.offer_price && (
                        <Grid item xs={12} md={4}>
                          <Typography variant="caption" color="text.secondary">
                            Offer Price:
                          </Typography>
                          <Typography variant="body2" fontWeight={600}>
                            ${deal.offer_price.toLocaleString()}
                          </Typography>
                        </Grid>
                      )}
                    </Grid>
                    {deal.notes && (
                      <Box sx={{ mt: 2, pt: 2, borderTop: 1, borderColor: "divider" }}>
                        <Typography variant="body2" color="text.secondary">
                          {deal.notes}
                        </Typography>
                      </Box>
                    )}
                    <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mt: 2 }}>
                      <Typography variant="caption" color="text.secondary">
                        Created: {new Date(deal.created_at).toLocaleString()}
                      </Typography>
                      {getNavigationHint(deal.status) && (
                        <Typography variant="caption" color="primary" fontWeight={600}>
                          {getNavigationHint(deal.status)} →
                        </Typography>
                      )}
                    </Box>
                  </Card.Body>
                </Card>
              </Grid>
            );
            })}
          </Grid>
        )}
      </Container>
    </Box>
  );
}
