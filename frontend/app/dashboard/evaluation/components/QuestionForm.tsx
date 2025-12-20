import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  RadioGroup,
  FormControlLabel,
  Radio,
  FormControl,
  FormLabel,
  Alert,
} from '@mui/material';
import { Button } from '@/components';

interface Question {
  id: string;
  label: string;
  type: 'text' | 'radio' | 'number';
  options?: string[];
  required?: boolean;
}

interface QuestionFormProps {
  questions: Question[];
  onSubmit: (answers: Record<string, string | number>) => void;
  onSkip?: () => void;
  loading?: boolean;
  error?: string | null;
}

export const QuestionForm: React.FC<QuestionFormProps> = ({
  questions,
  onSubmit,
  onSkip,
  loading = false,
  error = null,
}) => {
  const [answers, setAnswers] = useState<Record<string, string | number>>({});
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>(
    {}
  );

  const handleChange = (questionId: string, value: string | number) => {
    setAnswers((prev) => ({ ...prev, [questionId]: value }));
    // Clear validation error when user types
    if (validationErrors[questionId]) {
      setValidationErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[questionId];
        return newErrors;
      });
    }
  };

  const validate = (): boolean => {
    const errors: Record<string, string> = {};

    questions.forEach((question) => {
      if (question.required && !answers[question.id]) {
        errors[question.id] = 'This field is required';
      }
    });

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (validate()) {
      onSubmit(answers);
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Answer the following questions
        </Typography>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        <Box component="form" onSubmit={handleSubmit}>
          {questions.map((question) => (
            <Box key={question.id} sx={{ mb: 3 }}>
              {question.type === 'text' && (
                <TextField
                  fullWidth
                  label={question.label}
                  required={question.required}
                  value={answers[question.id] || ''}
                  onChange={(e) => handleChange(question.id, e.target.value)}
                  error={!!validationErrors[question.id]}
                  helperText={validationErrors[question.id]}
                  disabled={loading}
                />
              )}
              {question.type === 'number' && (
                <TextField
                  fullWidth
                  type="number"
                  label={question.label}
                  required={question.required}
                  value={answers[question.id] || ''}
                  onChange={(e) =>
                    handleChange(question.id, parseFloat(e.target.value))
                  }
                  error={!!validationErrors[question.id]}
                  helperText={validationErrors[question.id]}
                  disabled={loading}
                />
              )}
              {question.type === 'radio' && question.options && (
                <FormControl
                  component="fieldset"
                  required={question.required}
                  error={!!validationErrors[question.id]}
                  disabled={loading}
                >
                  <FormLabel component="legend">{question.label}</FormLabel>
                  <RadioGroup
                    value={answers[question.id] || ''}
                    onChange={(e) => handleChange(question.id, e.target.value)}
                  >
                    {question.options.map((option) => (
                      <FormControlLabel
                        key={option}
                        value={option}
                        control={<Radio />}
                        label={option}
                      />
                    ))}
                  </RadioGroup>
                  {validationErrors[question.id] && (
                    <Typography variant="caption" color="error">
                      {validationErrors[question.id]}
                    </Typography>
                  )}
                </FormControl>
              )}
            </Box>
          ))}
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
            {onSkip && (
              <Button
                variant="outline"
                size="lg"
                onClick={onSkip}
                disabled={loading}
              >
                Skip
              </Button>
            )}
            <Button
              variant="primary"
              size="lg"
              type="submit"
              disabled={loading}
              isLoading={loading}
            >
              Continue
            </Button>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};
