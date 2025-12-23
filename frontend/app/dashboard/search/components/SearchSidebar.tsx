import { Box, Paper, Typography, Alert } from "@mui/material";

export function SearchSidebar() {
  return (
    <Box sx={{ position: "sticky", top: 100 }}>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          💡 Financing Tips
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          • 20% down payment typically gets better rates
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          • Shorter loans save on total interest
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          • Check your credit score before applying
        </Typography>
        <Typography variant="body2" color="text.secondary">
          • Get pre-approved for better negotiation power
        </Typography>
      </Paper>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          🤖 AI Analysis
        </Typography>
        <Typography variant="body2" color="text.secondary">
          <strong>Max Results</strong> is used to fetch data from the Market Check API. The AI then analyzes this data to recommend the <strong>top 5</strong> vehicles for you.
        </Typography>
      </Paper>

      <Alert severity="info">
        <Typography variant="body2">
          <strong>Pro Tip:</strong> Knowing your financing options before
          shopping gives you better negotiating power with dealers.
        </Typography>
      </Alert>
    </Box>
  );
}
