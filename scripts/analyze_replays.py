import os
import glob
import pandas as pd
import json

def parse_quality(quality_str):
    if not isinstance(quality_str, str) or not quality_str.strip():
        return {}
    try:
        return json.loads(quality_str)
    except:
        return {}

def analyze_file(filepath):
    print(f"Analyzing {filepath}...")
    
    # Read first line to get columns
    df_temp = pd.read_csv(filepath, nrows=1)
    available_cols = set(df_temp.columns)
    
    # We load only the intersection of required and available columns
    cols_to_load = [
        'engine_version', 'ticker', 'analysis_date', 'signal', 'score', 'qualified', 'rank',
        'forward_return_pct', 'market_benchmark_return_pct', 'excess_return_pct', 
        'max_upside_pct', 'max_drawdown_pct', 'correct', 'analysis_quality_json'
    ]
    cols_to_load = [c for c in cols_to_load if c in available_cols]
    
    df = pd.read_csv(filepath, usecols=cols_to_load)
    
    # Fill in missing columns with safe defaults
    if 'rank' not in df.columns:
        df['rank'] = 999
    if 'analysis_quality_json' not in df.columns:
        df['analysis_quality_json'] = '{}'
    if 'qualified' not in df.columns:
        df['qualified'] = True
    if 'correct' not in df.columns:
        df['correct'] = True
        
    stats = {}
    stats['filename'] = os.path.basename(filepath)
    stats['total_rows'] = len(df)
    
    # Date Range
    df['analysis_date'] = pd.to_datetime(df['analysis_date'], errors='coerce')
    stats['date_min'] = df['analysis_date'].min().strftime('%Y-%m-%d') if not pd.isnull(df['analysis_date'].min()) else None
    stats['date_max'] = df['analysis_date'].max().strftime('%Y-%m-%d') if not pd.isnull(df['analysis_date'].max()) else None
    
    # Versions
    versions = df['engine_version'].dropna().unique().tolist() if 'engine_version' in df.columns else ['unknown']
    stats['versions'] = versions
    primary_version = versions[0] if len(versions) > 0 else 'unknown'
    
    # Convert numeric columns
    for num_col in ['forward_return_pct', 'market_benchmark_return_pct', 'excess_return_pct', 'max_upside_pct', 'max_drawdown_pct', 'score', 'rank']:
        if num_col in df.columns:
            df[num_col] = pd.to_numeric(df[num_col], errors='coerce')
            
    # Parse quality json
    df['parsed_quality'] = df['analysis_quality_json'].apply(parse_quality)
    
    # Classify row
    df['category'] = 'other'
    df.loc[df['signal'] == 'BUY', 'category'] = 'regular_buy'
    
    if primary_version in ('core-v2.5', 'core-v2.3'):
        def get_profile(quality_dict):
            elite = quality_dict.get('elite_assessment', {})
            if isinstance(elite, dict):
                return elite.get('selected_profile', 'none')
            return 'none'
        df['selected_profile'] = df['parsed_quality'].apply(get_profile)
        df.loc[(df['signal'] == 'BUY') & (df['selected_profile'] == 'balanced'), 'category'] = 'balanced_elite'
        df.loc[(df['signal'] == 'BUY') & (df['selected_profile'] == 'aggressive'), 'category'] = 'aggressive_elite'
        
    elif primary_version == 'core-v2.2':
        def get_v22_ready(quality_dict):
            elite = quality_dict.get('elite_assessment', {})
            if isinstance(elite, dict):
                return elite.get('engine_ready', False)
            return False
        df['is_elite'] = df['parsed_quality'].apply(get_v22_ready)
        df.loc[(df['signal'] == 'BUY') & (df['is_elite'] == True), 'category'] = 'balanced_elite'
        
    elif primary_version == 'core-v2.1' or primary_version == 'core-v2.0' or primary_version == 'unknown':
        df['qualified_bool'] = df['qualified'].astype(str).str.upper().isin(['TRUE', '1', '1.0'])
        df.loc[
            (df['signal'] == 'BUY') & 
            (df['rank'] <= 10) & 
            (df['qualified_bool'] == True) & 
            (df['score'] >= 80.0), 
            'category'
        ] = 'balanced_elite'
        
    # Group by category and compute stats
    category_groups = df.groupby('category')
    group_stats = {}
    
    # Value counts
    stats['signals'] = df['signal'].value_counts().to_dict() if 'signal' in df.columns else {}
    stats['categories'] = df['category'].value_counts().to_dict()
    
    for name, group in category_groups:
        if name == 'other':
            continue
        g_data = {}
        g_data['count'] = len(group)
        
        # Mean returns
        for metric in ['forward_return_pct', 'excess_return_pct', 'max_upside_pct', 'max_drawdown_pct']:
            if metric in group.columns:
                non_null = group[metric].dropna()
                if len(non_null) > 0:
                    g_data[f'{metric}_mean'] = float(non_null.mean())
                    g_data[f'{metric}_median'] = float(non_null.median())
                    
        # Win Rate (forward_return > 0)
        if 'forward_return_pct' in group.columns:
            ret_non_null = group['forward_return_pct'].dropna()
            if len(ret_non_null) > 0:
                g_data['win_rate'] = float((ret_non_null > 0).mean())
                
        # Correct rate
        if 'correct' in group.columns:
            corr_col = group['correct'].dropna()
            if len(corr_col) > 0:
                corr_bool = corr_col.astype(str).str.upper().isin(['TRUE', '1', '1.0'])
                g_data['correct_rate'] = float(corr_bool.mean())
                
        group_stats[name] = g_data
        
    stats['group_metrics'] = group_stats
    return stats

def main():
    files = glob.glob('sahmi-engine/*.csv')
    print(f"Found {len(files)} CSV files.")
    results = []
    for f in sorted(files):
        try:
            res = analyze_file(f)
            results.append(res)
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Failed to analyze {f}: {e}")
            
    # Write summary report
    output_path = 'sahmi-engine/replay_analysis_summary.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
        
    print(f"Analysis saved to {output_path}")

if __name__ == '__main__':
    main()
