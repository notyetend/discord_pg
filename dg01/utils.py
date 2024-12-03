import pandas as pd
import requests
from urllib.parse import urlparse, parse_qs
from io import StringIO


def download_google_sheet(sheet_url, output_filename='output.csv'):
    """
    구글 스프레드시트 URL에서 데이터를 다운로드하여 CSV 파일로 저장합니다.
    
    Parameters:
        sheet_url (str): 구글 스프레드시트 공유 URL
        output_filename (str): 저장할 CSV 파일명 (기본값: 'output.csv')
    """
    try:
        # URL이 올바른 구글 스프레드시트 주소인지 확인
        if 'docs.google.com/spreadsheets' not in sheet_url:
            raise ValueError('올바른 구글 스프레드시트 URL이 아닙니다.')
            
        # URL에서 스프레드시트 ID 추출
        parsed_url = urlparse(sheet_url)
        if 'spreadsheets/d/' in sheet_url:
            sheet_id = sheet_url.split('spreadsheets/d/')[1].split('/')[0]
        else:
            query_params = parse_qs(parsed_url.query)
            sheet_id = query_params.get('id', [None])[0]
            
        if not sheet_id:
            raise ValueError('스프레드시트 ID를 찾을 수 없습니다.')
        
        # CSV 다운로드 URL 생성
        csv_export_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv'
        
        # 데이터 다운로드
        response = requests.get(csv_export_url)
        response.raise_for_status()  # HTTP 에러 체크
        
        # CSV 파일로 저장
        with open(output_filename, 'wb') as f:
            f.write(response.content)
            
        print(f'데이터가 성공적으로 {output_filename}에 저장되었습니다.')
        
        # pandas로 데이터 읽기 (옵션)
        df = pd.read_csv(output_filename)
        return df.head()
        
    except requests.exceptions.RequestException as e:
        print(f'다운로드 중 오류가 발생했습니다: {e}')
    except ValueError as e:
        print(f'URL 처리 중 오류가 발생했습니다: {e}')
    except Exception as e:
        print(f'예상치 못한 오류가 발생했습니다: {e}')


def get_google_sheet_df(sheet_url, sheet_name=None):
    """
    구글 스프레드시트 URL에서 데이터를 다운로드하여 pandas DataFrame으로 반환합니다.
    
    Parameters:
        sheet_url (str): 구글 스프레드시트 공유 URL
        sheet_name (str): 가져올 시트 이름 (기본값: None, 첫 번째 시트를 가져옴)
    
    Returns:
        pandas.DataFrame: 스프레드시트 데이터를 담은 DataFrame
    """
    try:
        # URL이 올바른 구글 스프레드시트 주소인지 확인
        if 'docs.google.com/spreadsheets' not in sheet_url:
            raise ValueError('올바른 구글 스프레드시트 URL이 아닙니다.')
            
        # URL에서 스프레드시트 ID 추출
        parsed_url = urlparse(sheet_url)
        if 'spreadsheets/d/' in sheet_url:
            sheet_id = sheet_url.split('spreadsheets/d/')[1].split('/')[0]
        else:
            query_params = parse_qs(parsed_url.query)
            sheet_id = query_params.get('id', [None])[0]
            
        if not sheet_id:
            raise ValueError('스프레드시트 ID를 찾을 수 없습니다.')
        
        # CSV 다운로드 URL 생성 (시트 이름 포함)
        csv_export_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv'
        if sheet_name:
            csv_export_url += f'&gid={get_sheet_id(sheet_id, sheet_name)}'
        
        # 데이터 다운로드
        response = requests.get(csv_export_url)
        response.raise_for_status()  # HTTP 에러 체크
        
        # response의 인코딩을 UTF-8로 설정
        response.encoding = 'utf-8'
        
        # DataFrame으로 변환하여 반환 (encoding 파라미터 추가)
        return pd.read_csv(StringIO(response.text), encoding='utf-8')
        
    except requests.exceptions.RequestException as e:
        print(f'다운로드 중 오류가 발생했습니다: {e}')
    except ValueError as e:
        print(f'URL 처리 중 오류가 발생했습니다: {e}')
    except Exception as e:
        print(f'예상치 못한 오류가 발생했습니다: {e}')

def get_sheet_id(spreadsheet_id, sheet_name):
    """
    시트 이름으로부터 시트 ID(gid)를 가져옵니다.
    
    Parameters:
        spreadsheet_id (str): 스프레드시트 ID
        sheet_name (str): 시트 이름
    
    Returns:
        str: 시트 ID (gid)
    """
    try:
        # 스프레드시트 메타데이터 URL
        url = f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit/sheet?format=json'
        response = requests.get(url)
        response.raise_for_status()
        
        # JSON 응답에서 시트 정보 파싱
        sheet_data = response.json()
        for sheet in sheet_data.get('sheets', []):
            if sheet['properties']['title'] == sheet_name:
                return sheet['properties']['sheetId']
        
        raise ValueError(f'시트 "{sheet_name}"를 찾을 수 없습니다.')
        
    except Exception as e:
        print(f'시트 ID를 가져오는 중 오류가 발생했습니다: {e}')
        return None
        
    
        
# 사용 예시
if __name__ == '__main__':
    sheet_url = '구글 스프레드시트 URL을 여기에 입력하세요'
    df = download_google_sheet(sheet_url, 'downloaded_data.csv')