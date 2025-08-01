import os
from argparse import ArgumentParser

from dotenv import load_dotenv
from tqdm import tqdm
from web3 import Web3

# --- Цветовые константы для интерфейса анализатора ---
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def establish_chronolink():
    """Устанавливает связь с архивом блоков Ethereum."""
    load_dotenv()
    infura_project_id = os.getenv("INFURA_PROJECT_ID")
    if not infura_project_id or infura_project_id == "YOUR_INFURA_PROJECT_ID_HERE":
        print(f"{Colors.FAIL}Ошибка связи: INFURA_PROJECT_ID не настроен.{Colors.ENDC}")
        print(f"Требуется конфигурация. Создайте файл {Colors.BOLD}.env{Colors.ENDC} с вашим ключом доступа.")
        print("Формат: INFURA_PROJECT_ID=\"abcdef1234567890\"")
        return None
    
    w3 = Web3(Web3.HTTPProvider(f'https://mainnet.infura.io/v3/{infura_project_id}'))
    
    if not w3.is_connected():
        print(f"{Colors.FAIL}Не удалось подключиться к архиву Ethereum.{Colors.ENDC}")
        return None
        
    print(f"{Colors.GREEN}Связь с архивом Ethereum установлена. ChronoGraph готов к анализу.{Colors.ENDC}")
    return w3

def analyze_timeline(w3, artifact_address, period_in_blocks):
    """
    Реконструирует и анализирует временную линию взаимодействий с артефактом (контрактом).
    """
    try:
        target_artifact = w3.to_checksum_address(artifact_address)
    except ValueError:
        print(f"{Colors.FAIL}Ошибка идентификации: неверный формат адреса артефакта.{Colors.ENDC}")
        return

    latest_block_number = w3.eth.block_number
    start_block = latest_block_number - period_in_blocks + 1

    print(f"\n{Colors.HEADER}{Colors.BOLD}📜 Активация ChronoGraph... Реконструкция временной линии.{Colors.ENDC}")
    print(f"ИССЛЕДУЕМЫЙ АРТЕФАКТ:{Colors.CYAN} {target_artifact}{Colors.ENDC}")
    print(f"АНАЛИЗИРУЕМЫЙ ПЕРИОД:{Colors.CYAN} {period_in_blocks} блоков (эпоха с {start_block} по {latest_block_number}){Colors.ENDC}")
    
    actors_in_period = set()
    total_events = 0

    pbar = tqdm(range(start_block, latest_block_number + 1), 
                desc=f"{Colors.BLUE}Обработка хроники{Colors.ENDC}",
                ncols=100)

    for block_num in pbar:
        try:
            block = w3.eth.get_block(block_num, full_transactions=True)
            for tx in block.transactions:
                if tx['to'] and w3.to_checksum_address(tx['to']) == target_artifact:
                    total_events += 1
                    # "Актер" - это уникальный участник событий
                    actor = w3.to_checksum_address(tx['from'])
                    actors_in_period.add(actor)
        except Exception as e:
            tqdm.write(f"{Colors.WARNING}Поврежденный сектор в хронике {block_num}: {e}{Colors.ENDC}")
            continue

    # --- РАСЧЕТ ИСТОРИЧЕСКИХ МЕТРИК ---
    total_unique_actors = len(actors_in_period)
    
    # Симуляция. "Новые" актеры - это все, кто появился в данный исторический период.
    # Продвинутая версия сравнивала бы с базой данных актеров из предыдущих "эпох".
    known_actors_from_past = set() 
    first_time_actors = actors_in_period - known_actors_from_past
    
    # Наша ключевая метрика: Коэффициент Появления!
    emergence_coefficient = (len(first_time_actors) / total_unique_actors) * 100 if total_unique_actors > 0 else 0

    # --- ВЫВОД ИСТОРИЧЕСКОГО ОТЧЕТА ---
    print(f"\n{Colors.HEADER}{Colors.BOLD}📖 Исторический отчет ChronoGraph:{Colors.ENDC}")
    print("=" * 60)
    print(f"Всего событий за период: {Colors.BOLD}{Colors.GREEN}{total_events}{Colors.ENDC}")
    print(f"Уникальных актеров (участников): {Colors.BOLD}{Colors.GREEN}{total_unique_actors}{Colors.ENDC}")
    
    print(f"\n{Colors.HEADER}{Colors.UNDERLINE}Ключевой исторический показатель:{Colors.ENDC}")
    print(f"✨ {Colors.WARNING}Коэффициент Появления (Emergence Coefficient):{Colors.ENDC} "
          f"{Colors.BOLD}{emergence_coefficient:.2f}%{Colors.ENDC}")
    print(f"   {Colors.WARNING}(Доля новых актеров, впервые появившихся на сцене){Colors.ENDC}")
    print("=" * 60)
    
    if emergence_coefficient > 80:
         print(f"{Colors.GREEN}ИСТОРИЧЕСКИЙ ВЕРДИКТ: 'Ренессанс'. Период взрывного роста и появления множества новых действующих лиц.{Colors.ENDC}")
    elif emergence_coefficient > 50:
        print(f"{Colors.CYAN}ИСТОРИЧЕСКИЙ ВЕРДИКТ: 'Эпоха Просвещения'. Стабильный приток новых идей и участников.{Colors.ENDC}")
    else:
        print(f"{Colors.BLUE}ИСТОРИЧЕСКИЙ ВЕРДИКТ: 'Классический период'. История пишется устоявшимся кругом актеров.{Colors.ENDC}")


if __name__ == "__main__":
    parser = ArgumentParser(description="ChronoGraph - анализатор временной линии для исследования ончейн-артефактов.")
    parser.add_argument("artifact", help="Адрес артефакта (смарт-контракта) для исследования.")
    parser.add_argument("-p", "--period", type=int, default=1000, help="Длительность исследуемого периода в блоках (по умолчанию: 1000).")
    
    args = parser.parse_args()
    
    chronolink = establish_chronolink()
    if chronolink:
        analyze_timeline(chronolink, args.artifact, args.period)
