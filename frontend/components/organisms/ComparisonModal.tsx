'use client';

import React from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Chip from '@mui/material/Chip';
import Stack from '@mui/material/Stack';
import { Modal } from '@/components';
import { ComparisonVehicle } from '@/lib/hooks/useComparison';

interface ComparisonModalProps {
  isOpen: boolean;
  onClose: () => void;
  vehicles: ComparisonVehicle[];
}

export const ComparisonModal: React.FC<ComparisonModalProps> = ({
  isOpen,
  onClose,
  vehicles,
}) => {
  if (vehicles.length === 0) {
    return null;
  }

  const comparisonRows = [
    { label: 'Image', key: 'image' },
    { label: 'Vehicle', key: 'name' },
    { label: 'Price', key: 'price' },
    { label: 'Year', key: 'year' },
    { label: 'Mileage', key: 'mileage' },
    { label: 'Fuel Type', key: 'fuelType' },
    { label: 'Transmission', key: 'transmission' },
    { label: 'Condition', key: 'condition' },
    { label: 'Recommendation Score', key: 'recommendation_score' },
    { label: 'Features', key: 'highlights' },
  ];

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Vehicle Comparison" size="xl">
      <Box sx={{ p: 2 }}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell sx={{ fontWeight: 600, minWidth: 150 }}>Feature</TableCell>
                {vehicles.map((vehicle) => (
                  <TableCell key={vehicle.vin} align="center" sx={{ minWidth: 200 }}>
                    <Box
                      sx={{
                        width: '100%',
                        height: 120,
                        backgroundImage: `url(${vehicle.image})`,
                        backgroundSize: 'cover',
                        backgroundPosition: 'center',
                        borderRadius: 1,
                        mb: 1,
                      }}
                    />
                    <Typography variant="subtitle2" fontWeight={600}>
                      {vehicle.year} {vehicle.make}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {vehicle.model}
                    </Typography>
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {comparisonRows.map((row) => {
                if (row.key === 'image' || row.key === 'name') return null;

                return (
                  <TableRow key={row.key}>
                    <TableCell sx={{ fontWeight: 600 }}>{row.label}</TableCell>
                    {vehicles.map((vehicle) => (
                      <TableCell key={vehicle.vin} align="center">
                        {row.key === 'price' && (
                          <Typography variant="h6" color="primary" fontWeight={700}>
                            ${vehicle.price.toLocaleString()}
                          </Typography>
                        )}
                        {row.key === 'year' && (
                          <Typography variant="body1">{vehicle.year}</Typography>
                        )}
                        {row.key === 'mileage' && (
                          <Typography variant="body1">
                            {vehicle.mileage.toLocaleString()} mi
                          </Typography>
                        )}
                        {row.key === 'fuelType' && (
                          <Chip label={vehicle.fuelType || 'N/A'} size="small" />
                        )}
                        {row.key === 'transmission' && (
                          <Chip label={vehicle.transmission || 'N/A'} size="small" />
                        )}
                        {row.key === 'condition' && (
                          <Chip
                            label={vehicle.condition || 'Used'}
                            size="small"
                            color="primary"
                          />
                        )}
                        {row.key === 'recommendation_score' && (
                          <Box>
                            {vehicle.recommendation_score ? (
                              <Chip
                                label={`${vehicle.recommendation_score.toFixed(1)}/10`}
                                size="small"
                                color="success"
                              />
                            ) : (
                              <Typography variant="body2" color="text.secondary">
                                N/A
                              </Typography>
                            )}
                          </Box>
                        )}
                        {row.key === 'highlights' && (
                          <Stack spacing={0.5} alignItems="center">
                            {vehicle.highlights && vehicle.highlights.length > 0 ? (
                              vehicle.highlights.slice(0, 5).map((highlight, idx) => (
                                <Chip
                                  key={idx}
                                  label={highlight}
                                  size="small"
                                  variant="outlined"
                                />
                              ))
                            ) : (
                              <Typography variant="body2" color="text.secondary">
                                No features listed
                              </Typography>
                            )}
                          </Stack>
                        )}
                      </TableCell>
                    ))}
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </TableContainer>
      </Box>
    </Modal>
  );
};
