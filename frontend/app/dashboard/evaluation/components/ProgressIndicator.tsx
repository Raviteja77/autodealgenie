import React from 'react';
import { Box, Step, StepLabel, Stepper, Typography } from '@mui/material';
import {
  AssignmentOutlined,
  AttachMoneyOutlined,
  AccountBalanceOutlined,
  WarningAmberOutlined,
  CheckCircleOutlineOutlined,
} from '@mui/icons-material';
import { PipelineStep } from '@/lib/api';

interface ProgressIndicatorProps {
  currentStep: PipelineStep;
  completedSteps: PipelineStep[];
}

const STEPS: Array<{ key: PipelineStep; label: string; icon: React.ReactElement }> = [
  {
    key: 'vehicle_condition',
    label: 'Condition',
    icon: <AssignmentOutlined />,
  },
  {
    key: 'price',
    label: 'Price',
    icon: <AttachMoneyOutlined />,
  },
  {
    key: 'financing',
    label: 'Finance',
    icon: <AccountBalanceOutlined />,
  },
  {
    key: 'risk',
    label: 'Risk',
    icon: <WarningAmberOutlined />,
  },
  {
    key: 'final',
    label: 'Final',
    icon: <CheckCircleOutlineOutlined />,
  },
];

export const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({
  currentStep,
  completedSteps,
}) => {
  const currentStepIndex = STEPS.findIndex((step) => step.key === currentStep);

  return (
    <Box sx={{ width: '100%', mb: 4 }}>
      <Stepper activeStep={currentStepIndex} alternativeLabel>
        {STEPS.map((step) => {
          const isCompleted = completedSteps.includes(step.key);
          const isCurrent = step.key === currentStep;

          return (
            <Step key={step.key} completed={isCompleted}>
              <StepLabel
                StepIconComponent={() => (
                  <Box
                    sx={{
                      width: 40,
                      height: 40,
                      borderRadius: '50%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      bgcolor: isCompleted
                        ? 'success.main'
                        : isCurrent
                        ? 'primary.main'
                        : 'grey.300',
                      color: isCompleted || isCurrent ? 'white' : 'grey.600',
                    }}
                  >
                    {step.icon}
                  </Box>
                )}
              >
                <Typography
                  variant="caption"
                  sx={{
                    fontWeight: isCurrent ? 600 : 400,
                    color: isCurrent ? 'primary.main' : 'text.secondary',
                  }}
                >
                  {step.label}
                </Typography>
              </StepLabel>
            </Step>
          );
        })}
      </Stepper>
    </Box>
  );
};
