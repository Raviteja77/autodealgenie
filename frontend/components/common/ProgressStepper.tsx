"use client";

import { Stepper, Step, StepLabel, Box, StepConnector, styled } from "@mui/material";
import { Check } from "@mui/icons-material";
import { StepIconProps } from "@mui/material/StepIcon";

interface ProgressStepperProps {
  activeStep: number;
  steps: string[];
}

// Shared gradient constant
const BLUE_GRADIENT = "linear-gradient(95deg, rgb(37,99,235) 0%, rgb(59,130,246) 50%, rgb(96,165,250) 100%)";
const BLUE_GRADIENT_ICON = "linear-gradient(136deg, rgb(37,99,235) 0%, rgb(59,130,246) 50%, rgb(96,165,250) 100%)";

const ColorlibConnector = styled(StepConnector)(({ theme }) => ({
  alternativeLabel: {
    top: 22,
  },
  active: {
    "& .MuiStepConnector-line": {
      backgroundImage: BLUE_GRADIENT,
    },
  },
  completed: {
    "& .MuiStepConnector-line": {
      backgroundImage: BLUE_GRADIENT,
    },
  },
  line: {
    height: 3,
    border: 0,
    backgroundColor:
      theme.palette.mode === "dark" ? theme.palette.grey[800] : "#eaeaf0",
    borderRadius: 1,
  },
}));

const ColorlibStepIconRoot = styled("div")<{
  ownerState: { completed?: boolean; active?: boolean };
}>(({ theme, ownerState }) => ({
  backgroundColor:
    theme.palette.mode === "dark" ? theme.palette.grey[700] : "#ccc",
  zIndex: 1,
  color: "#fff",
  width: 50,
  height: 50,
  display: "flex",
  borderRadius: "50%",
  justifyContent: "center",
  alignItems: "center",
  ...(ownerState.active && {
    backgroundImage: BLUE_GRADIENT_ICON,
    boxShadow: "0 4px 10px 0 rgba(0,0,0,.25)",
  }),
  ...(ownerState.completed && {
    backgroundImage: BLUE_GRADIENT_ICON,
  }),
}));

function ColorlibStepIcon(props: StepIconProps) {
  const { active, completed, className } = props;

  return (
    <ColorlibStepIconRoot
      ownerState={{ completed, active }}
      className={className}
    >
      {completed ? (
        <Check sx={{ fontSize: 24 }} />
      ) : (
        <Box sx={{ fontSize: 20, fontWeight: "bold" }}>{String(props.icon)}</Box>
      )}
    </ColorlibStepIconRoot>
  );
}

export default function ProgressStepper({
  activeStep,
  steps,
}: ProgressStepperProps) {
  return (
    <Box sx={{ width: "100%", mb: 4 }}>
      <Stepper
        alternativeLabel
        activeStep={activeStep}
        connector={<ColorlibConnector />}
      >
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel StepIconComponent={ColorlibStepIcon}>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>
    </Box>
  );
}
