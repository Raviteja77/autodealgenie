// components/molecules/Pagination/Pagination.tsx
import { FC } from 'react';
import { Box, IconButton, Typography, Select, MenuItem } from '@mui/material';
import {
  ChevronLeft,
  ChevronRight,
  FirstPage,
  LastPage,
} from '@mui/icons-material';

export interface PaginationProps {
  currentPage: number;
  totalPages: number;
  totalItems?: number;
  itemsPerPage?: number;
  onPageChange: (page: number) => void;
  onItemsPerPageChange?: (itemsPerPage: number) => void;
  itemsPerPageOptions?: number[];
  showItemsPerPage?: boolean;
}

export const Pagination: FC<PaginationProps> = ({
  currentPage,
  totalPages,
  totalItems,
  itemsPerPage = 12,
  onPageChange,
  onItemsPerPageChange,
  itemsPerPageOptions = [12, 24, 36, 48],
  showItemsPerPage = true,
}) => {
  const startItem = (currentPage - 1) * itemsPerPage + 1;
  const endItem = Math.min(currentPage * itemsPerPage, totalItems || 0);

  const handleFirstPage = () => onPageChange(1);
  const handlePrevPage = () => onPageChange(Math.max(1, currentPage - 1));
  const handleNextPage = () => onPageChange(Math.min(totalPages, currentPage + 1));
  const handleLastPage = () => onPageChange(totalPages);

  if (totalPages <= 1) return null;

  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        mt: 4,
        pt: 3,
        borderTop: 1,
        borderColor: 'divider',
        flexWrap: 'wrap',
        gap: 2,
      }}
    >
      {/* Items info */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        {totalItems && (
          <Typography variant="body2" color="text.secondary">
            Showing {startItem}-{endItem} of {totalItems} vehicles
          </Typography>
        )}

        {showItemsPerPage && onItemsPerPageChange && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="body2" color="text.secondary">
              Per page:
            </Typography>
            <Select
              value={itemsPerPage}
              onChange={(e) => onItemsPerPageChange(Number(e.target.value))}
              size="small"
              sx={{ minWidth: 70 }}
            >
              {itemsPerPageOptions.map((option) => (
                <MenuItem key={option} value={option}>
                  {option}
                </MenuItem>
              ))}
            </Select>
          </Box>
        )}
      </Box>

      {/* Page controls */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <IconButton
          onClick={handleFirstPage}
          disabled={currentPage === 1}
          size="small"
          aria-label="First page"
        >
          <FirstPage />
        </IconButton>
        <IconButton
          onClick={handlePrevPage}
          disabled={currentPage === 1}
          size="small"
          aria-label="Previous page"
        >
          <ChevronLeft />
        </IconButton>

        <Typography variant="body2" sx={{ mx: 2, minWidth: 100, textAlign: 'center' }}>
          Page {currentPage} of {totalPages}
        </Typography>

        <IconButton
          onClick={handleNextPage}
          disabled={currentPage === totalPages}
          size="small"
          aria-label="Next page"
        >
          <ChevronRight />
        </IconButton>
        <IconButton
          onClick={handleLastPage}
          disabled={currentPage === totalPages}
          size="small"
          aria-label="Last page"
        >
          <LastPage />
        </IconButton>
      </Box>
    </Box>
  );
};