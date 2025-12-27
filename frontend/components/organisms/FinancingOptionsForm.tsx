import {
  Typography,
  Grid,
  Paper,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Tooltip,
  IconButton,
} from "@mui/material";
import { Info as InfoIcon } from "@mui/icons-material";
import { Input } from "@/components";

interface FinancingOptionsFormProps {
  downPayment?: number;
  tradeInValue?: number;
  loanTerm?: number;
  creditScore?: "excellent" | "good" | "fair" | "poor";
  monthlyPaymentMax?: number;
  estimatedPayment: number | null;
  onDownPaymentChange: (value: number) => void;
  onTradeInValueChange: (value: number) => void;
  onLoanTermChange: (value: number) => void;
  onCreditScoreChange: (
    value: "excellent" | "good" | "fair" | "poor"
  ) => void;
  onMonthlyPaymentMaxChange: (value: number | undefined) => void;
  downPaymentError?: string;
}

export function FinancingOptionsForm({
  downPayment,
  tradeInValue,
  loanTerm,
  creditScore,
  monthlyPaymentMax,
  estimatedPayment,
  onDownPaymentChange,
  onTradeInValueChange,
  onLoanTermChange,
  onCreditScoreChange,
  onMonthlyPaymentMaxChange,
  downPaymentError,
}: FinancingOptionsFormProps) {
  return (
    <Paper
      variant="outlined"
      sx={{ p: 3, bgcolor: "primary.50", borderRadius: 2 }}
    >
      <Typography variant="h6" gutterBottom>
        Financing Details
        <Tooltip title="Provide financing details to see accurate monthly payment estimates">
          <IconButton size="small" sx={{ ml: 1 }}>
            <InfoIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Typography>

      <Grid container spacing={2} sx={{ mt: 1 }}>
        {/* Down Payment */}
        <Grid item xs={12} md={6}>
          <Input
            fullWidth
            label="Down Payment"
            type="number"
            value={downPayment || ""}
            onChange={(e) => onDownPaymentChange(parseInt(e.target.value) || 0)}
            placeholder="e.g., 5000"
            error={downPaymentError}
            aria-label="Down payment amount"
          />
        </Grid>

        {/* Trade-In Value */}
        <Grid item xs={12} md={6}>
          <Input
            fullWidth
            label="Trade-In Value (Optional)"
            type="number"
            value={tradeInValue || ""}
            onChange={(e) =>
              onTradeInValueChange(parseInt(e.target.value) || 0)
            }
            placeholder="e.g., 8000"
          />
        </Grid>

        {/* Loan Term */}
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel id="loan-term-label">Loan Term</InputLabel>
            <Select
              labelId="loan-term-label"
              value={loanTerm || ""}
              label="Loan Term"
              onChange={(e) => onLoanTermChange(e.target.value as number)}
              aria-label="Loan term selection"
            >
              <MenuItem value={36}>36 months (3 years)</MenuItem>
              <MenuItem value={48}>48 months (4 years)</MenuItem>
              <MenuItem value={60}>60 months (5 years)</MenuItem>
              <MenuItem value={72}>72 months (6 years)</MenuItem>
            </Select>
          </FormControl>
        </Grid>

        {/* Credit Score */}
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel id="credit-score-label">Credit Score Range</InputLabel>
            <Select
              labelId="credit-score-label"
              value={creditScore || ""}
              label="Credit Score Range"
              onChange={(e) =>
                onCreditScoreChange(
                  e.target.value as "excellent" | "good" | "fair" | "poor"
                )
              }
              aria-label="Credit score range selection"
            >
              <MenuItem value="excellent">Excellent (750+)</MenuItem>
              <MenuItem value="good">Good (700-749)</MenuItem>
              <MenuItem value="fair">Fair (650-699)</MenuItem>
              <MenuItem value="poor">{"Poor (< 650)"}</MenuItem>
            </Select>
          </FormControl>
        </Grid>

        {/* Maximum Monthly Payment */}
        <Grid item xs={12}>
          <Input
            fullWidth
            label="Maximum Monthly Payment (Optional)"
            type="number"
            value={monthlyPaymentMax || ""}
            onChange={(e) =>
              onMonthlyPaymentMaxChange(
                parseInt(e.target.value) || undefined
              )
            }
            placeholder="e.g., 500"
          />
        </Grid>

        {/* Estimated Payment Display */}
        {estimatedPayment && (
          <Grid item xs={12}>
            <Alert severity="info" sx={{ mt: 2 }}>
              <Typography variant="body2" gutterBottom>
                <strong>Estimated Monthly Payment:</strong>
              </Typography>
              <Typography variant="h5" color="primary">
                ${estimatedPayment}/month
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Based on average price in your range. Actual rates may vary.
              </Typography>
            </Alert>
          </Grid>
        )}
      </Grid>
    </Paper>
  );
}
