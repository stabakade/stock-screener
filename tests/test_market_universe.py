from src.data.universe_fetcher import (
    NSEStockUniverseFetcher,
    USStockUniverseFetcher,
    get_stock_universe_fetcher,
)
from src.screening.benchmark import format_benchmark_summary


def test_market_factory_selects_market_fetcher(tmp_path):
    assert isinstance(get_stock_universe_fetcher('us', str(tmp_path)), USStockUniverseFetcher)
    assert isinstance(get_stock_universe_fetcher('india', str(tmp_path)), NSEStockUniverseFetcher)


def test_nse_universe_formats_yahoo_symbols_and_keeps_eq_series(monkeypatch, tmp_path):
    csv_data = (
        'SYMBOL,NAME OF COMPANY, SERIES\n'
        'RELIANCE,Reliance Industries Limited, EQ\n'
        'M&M, Mahindra & Mahindra Limited,EQ\n'
        'ILLQ, Illiquid Example Limited,BE\n'
        'ETFTEST, Example Index ETF,EQ\n'
    ).encode()

    class Response:
        content = csv_data

        @staticmethod
        def raise_for_status():
            return None

    monkeypatch.setattr('src.data.universe_fetcher.requests.get', lambda *args, **kwargs: Response())
    fetcher = NSEStockUniverseFetcher(cache_dir=str(tmp_path))

    assert fetcher.fetch_universe() == ['M&M.NS', 'RELIANCE.NS']


def test_market_factory_rejects_unknown_market(tmp_path):
    try:
        get_stock_universe_fetcher('unknown', str(tmp_path))
    except ValueError as error:
        assert 'Unsupported market' in str(error)
    else:
        raise AssertionError('unsupported market should raise ValueError')


def test_india_benchmark_summary_uses_nifty_and_inr():
    summary = format_benchmark_summary(
        {
            'benchmark_ticker': '^NSEI',
            'phase': 2,
            'phase_name': 'Uptrend',
            'trend': 'Bullish',
            'confidence': 85,
            'current_price': 25000,
            'sma_50': 24500,
            'sma_200': 23000,
            'slope_50': 0.1,
            'slope_200': 0.05,
        },
        {
            'total_stocks': 1,
            'phase_1_count': 0,
            'phase_2_count': 1,
            'phase_3_count': 0,
            'phase_4_count': 0,
            'phase_1_pct': 0,
            'phase_2_pct': 100,
            'phase_3_pct': 0,
            'phase_4_pct': 0,
            'breadth_quality': 'Excellent',
        },
    )

    assert 'NIFTY 50 Trend Classification' in summary
    assert 'Current Price: ₹25000.00' in summary
    assert '50 SMA: ₹24500.00' in summary