// Currency formatting utilities for Maestro EGP

const CURRENCIES = {
  IQD: { code: 'IQD', name: 'دينار عراقي', symbol: 'د.ع', rate: 1 },
  USD: { code: 'USD', name: 'دولار أمريكي', symbol: '$', rate: 1460 },
};

/**
 * Format price in Iraqi Dinar
 * @param {number} amount - Amount in IQD
 * @param {boolean} showSymbol - Whether to show currency symbol
 * @returns {string} Formatted price
 */
export const formatPrice = (amount, showSymbol = true) => {
  if (amount === null || amount === undefined) return '0';
  
  const formatted = new Intl.NumberFormat('ar-IQ', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
  
  return showSymbol ? `${formatted} د.ع` : formatted;
};

/**
 * Format price with compact notation for large numbers
 * @param {number} amount - Amount in IQD
 * @returns {string} Formatted price
 */
export const formatPriceCompact = (amount) => {
  if (amount >= 1000000) {
    return `${(amount / 1000000).toFixed(1)}M د.ع`;
  }
  if (amount >= 1000) {
    return `${(amount / 1000).toFixed(0)}K د.ع`;
  }
  return formatPrice(amount);
};

/**
 * Convert between currencies
 * @param {number} amount - Amount to convert
 * @param {string} from - Source currency code
 * @param {string} to - Target currency code
 * @returns {number} Converted amount
 */
export const convertCurrency = (amount, from = 'IQD', to = 'USD') => {
  const fromCurrency = CURRENCIES[from];
  const toCurrency = CURRENCIES[to];
  
  if (!fromCurrency || !toCurrency) return amount;
  
  // Convert to IQD first, then to target currency
  const inIQD = amount * fromCurrency.rate;
  return inIQD / toCurrency.rate;
};

/**
 * Parse price string to number
 * @param {string} priceString - Price string to parse
 * @returns {number} Parsed number
 */
export const parsePrice = (priceString) => {
  if (typeof priceString === 'number') return priceString;
  if (!priceString) return 0;
  
  // Remove currency symbols and spaces
  const cleaned = priceString.replace(/[^\d.-]/g, '');
  return parseFloat(cleaned) || 0;
};

export default {
  formatPrice,
  formatPriceCompact,
  convertCurrency,
  parsePrice,
  CURRENCIES,
};
