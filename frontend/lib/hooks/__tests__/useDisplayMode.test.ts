import { renderHook, act } from '@testing-library/react';
import { useDisplayMode } from '../useDisplayMode';

describe('useDisplayMode', () => {
  it('initializes with default cash mode', () => {
    const { result } = renderHook(() => useDisplayMode());
    
    expect(result.current.displayMode).toBe('cash');
    expect(result.current.isCashMode).toBe(true);
    expect(result.current.isMonthlyMode).toBe(false);
  });

  it('initializes with specified default mode', () => {
    const { result } = renderHook(() => 
      useDisplayMode({ defaultMode: 'monthly' })
    );
    
    expect(result.current.displayMode).toBe('monthly');
    expect(result.current.isMonthlyMode).toBe(true);
  });

  it('toggles between modes', () => {
    const { result } = renderHook(() => useDisplayMode());
    
    act(() => {
      result.current.toggleMode();
    });
    
    expect(result.current.displayMode).toBe('monthly');
    
    act(() => {
      result.current.toggleMode();
    });
    
    expect(result.current.displayMode).toBe('cash');
  });

  it('sets to cash mode', () => {
    const { result } = renderHook(() => 
      useDisplayMode({ defaultMode: 'monthly' })
    );
    
    act(() => {
      result.current.setToCash();
    });
    
    expect(result.current.displayMode).toBe('cash');
  });

  it('sets to monthly mode', () => {
    const { result } = renderHook(() => useDisplayMode());
    
    act(() => {
      result.current.setToMonthly();
    });
    
    expect(result.current.displayMode).toBe('monthly');
  });

  it('does not toggle when allowToggle is false', () => {
    const { result } = renderHook(() => 
      useDisplayMode({ allowToggle: false })
    );
    
    act(() => {
      result.current.toggleMode();
    });
    
    expect(result.current.displayMode).toBe('cash');
  });
});
