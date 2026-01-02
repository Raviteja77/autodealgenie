"use client";

import { useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Box, Container, Typography, Chip, Grid } from "@mui/material";
import { apiClient, Deal } from "@/lib/api";
import { getUserFriendlyErrorMessage } from "@/lib/errors";
import { useApi, useFetchOnce } from "@/lib/hooks";
import {
  buildVehicleQueryString,
  ROUTES,
  FUEL_TYPE,
  VEHICLE_CONDITION,
  getStatusColor,
  getStatusLabel,
  getNavigationHint,
} from "@/lib/constants";
import { Button, Card, LoadingState, ErrorState, EmptyState } from "@/components";

export default function DealsPage() {
  const router = useRouter();
  const { data: deals, isLoading, error, execute } = useApi<Deal[]>();
  const { executeFetch, shouldFetch } = useFetchOnce();

  useEffect(() => {
    if (!shouldFetch()) return;
    
    executeFetch(() => execute(() => apiClient.getDeals()));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleDealClick = (deal: Deal) => {
    const finalPrice = deal.offer_price ?? deal.asking_price;
    
    const queryString = buildVehicleQueryString({
      vin: deal.vehicle_vin,
      make: deal.vehicle_make,
      model: deal.vehicle_model,
      year: deal.vehicle_year,
      price: finalPrice,
      mileage: deal.vehicle_mileage,
      fuelType: FUEL_TYPE.DEFAULT,
      condition: VEHICLE_CONDITION.DEFAULT,
      dealId: deal.id,
    });
    
    // Navigate based on deal status
    if (deal.status === "pending") {
      router.push(`${ROUTES.EVALUATION}?${queryString}`);
    } else if (deal.status === "in_progress") {
      router.push(`${ROUTES.NEGOTIATION}?${queryString}`);
    } else if (deal.status === "completed") {
      router.push(`${ROUTES.FINALIZE}?${queryString}`);
    }
  };

  if (isLoading) {
    return <LoadingState message="Loading deals..." />;
  }

  if (error) {
    return (
      <ErrorState
        title="Error Loading Deals"
        message={getUserFriendlyErrorMessage(error)}
        showRetry
        onRetry={() => execute(() => apiClient.getDeals())}
      />
    );
  }

  return (
    <Box sx={{ minHeight: "100vh", bgcolor: "background.default", py: 4 }}>
      <Container maxWidth="lg">
        {!deals || deals.length === 0 ? (
          <EmptyState
            message="No deals found"
            description="Start browsing vehicles and create your first deal"
            actionLabel="Search Vehicles"
            onAction={() => router.push(ROUTES.SEARCH)}
          />
        ) : (
          <Grid container spacing={3}>
            {deals.map((deal) => {
              return (
                <Grid item xs={12} key={deal.id}>
                  <Card 
                    hover={true} 
                    shadow="md" 
                    sx={{ cursor: "pointer" }} 
                    onClick={() => handleDealClick(deal)}
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
                        label={getStatusLabel(deal.status)}
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
