"""
State Management - Persistent Storage for Video Creation State
Inspirado em AWS DynamoDB, Azure Cosmos DB, Vertex AI Firestore
"""

import json
import sqlite3
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
import hashlib


# ============================================================================
# SQLITE STATE MANAGER (Default - Local Persistence)
# ============================================================================

class StateManager:
    """
    Gerenciador de estado persistente usando SQLite

    Features:
    - State persistence (não perde dados ao reiniciar)
    - Request history
    - Status tracking
    - Query capabilities
    - Lightweight (sem dependências)

    Similar a:
    - AWS DynamoDB (mas local)
    - Azure Cosmos DB (mas local)
    - Vertex Firestore (mas local)
    """

    def __init__(self, db_path: str = 'data/oma_state.db'):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._create_tables()

    def _create_tables(self):
        """Cria tabelas necessárias"""
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS video_requests (
                request_id TEXT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT NOT NULL,
                state_json TEXT NOT NULL,
                result_json TEXT,
                error TEXT,
                metadata_json TEXT
            )
        ''')

        # Índices para queries rápidas
        self.conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_status ON video_requests(status)
        ''')

        self.conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_created_at ON video_requests(created_at DESC)
        ''')

        self.conn.commit()

    def save_request(
        self,
        request_id: str,
        state: Dict[str, Any],
        status: str = 'in_progress',
        result: Optional[Dict] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """
        Salva ou atualiza request

        Args:
            request_id: ID único do request
            state: Estado atual (VideoState)
            status: pending, in_progress, completed, failed
            result: Resultado final (se completed)
            error: Mensagem de erro (se failed)
            metadata: Metadata adicional
        """
        self.conn.execute('''
            INSERT OR REPLACE INTO video_requests
            (request_id, updated_at, status, state_json, result_json, error, metadata_json)
            VALUES (?, datetime('now'), ?, ?, ?, ?, ?)
        ''', (
            request_id,
            status,
            json.dumps(state, ensure_ascii=False),
            json.dumps(result, ensure_ascii=False) if result else None,
            error,
            json.dumps(metadata, ensure_ascii=False) if metadata else None
        ))

        self.conn.commit()

    def get_request(self, request_id: str) -> Optional[Dict]:
        """Retorna request pelo ID"""
        cursor = self.conn.execute('''
            SELECT request_id, created_at, updated_at, status,
                   state_json, result_json, error, metadata_json
            FROM video_requests
            WHERE request_id = ?
        ''', (request_id,))

        row = cursor.fetchone()
        if not row:
            return None

        return {
            'request_id': row[0],
            'created_at': row[1],
            'updated_at': row[2],
            'status': row[3],
            'state': json.loads(row[4]) if row[4] else {},
            'result': json.loads(row[5]) if row[5] else None,
            'error': row[6],
            'metadata': json.loads(row[7]) if row[7] else None
        }

    def update_status(self, request_id: str, status: str, error: Optional[str] = None):
        """Atualiza apenas o status"""
        self.conn.execute('''
            UPDATE video_requests
            SET status = ?, updated_at = datetime('now'), error = ?
            WHERE request_id = ?
        ''', (status, error, request_id))

        self.conn.commit()

    def list_requests(
        self,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict]:
        """Lista requests com filtros"""
        query = '''
            SELECT request_id, created_at, updated_at, status
            FROM video_requests
        '''

        params = []

        if status:
            query += ' WHERE status = ?'
            params.append(status)

        query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
        params.extend([limit, offset])

        cursor = self.conn.execute(query, params)

        results = []
        for row in cursor.fetchall():
            results.append({
                'request_id': row[0],
                'created_at': row[1],
                'updated_at': row[2],
                'status': row[3]
            })

        return results

    def get_stats(self) -> Dict:
        """Retorna estatísticas gerais"""
        cursor = self.conn.execute('''
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) as in_progress,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending
            FROM video_requests
        ''')

        row = cursor.fetchone()

        return {
            'total': row[0],
            'completed': row[1],
            'failed': row[2],
            'in_progress': row[3],
            'pending': row[4],
            'success_rate': (row[1] / row[0] * 100) if row[0] > 0 else 0
        }

    def delete_request(self, request_id: str):
        """Deleta request"""
        self.conn.execute('DELETE FROM video_requests WHERE request_id = ?', (request_id,))
        self.conn.commit()

    def cleanup_old_requests(self, days: int = 30):
        """Remove requests antigos"""
        self.conn.execute('''
            DELETE FROM video_requests
            WHERE created_at < datetime('now', ?)
        ''', (f'-{days} days',))

        self.conn.commit()

    def close(self):
        """Fecha conexão"""
        self.conn.close()


# ============================================================================
# REDIS STATE MANAGER (Optional - For Production)
# ============================================================================

class RedisStateManager:
    """
    State manager usando Redis (para produção de alta performance)

    Vantagens vs SQLite:
    - Muito mais rápido
    - Shared entre múltiplos processos/servidores
    - TTL automático
    - Pub/Sub para eventos

    Requer: pip install redis
    """

    def __init__(self, host='localhost', port=6379, db=0, ttl=3600):
        """
        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
            ttl: Time to live em segundos (default: 1 hora)
        """
        try:
            import redis
            self.redis = redis.Redis(
                host=host,
                port=port,
                db=db,
                decode_responses=True
            )
            self.ttl = ttl
            self.enabled = True

            # Test connection
            self.redis.ping()

        except Exception as e:
            print(f"⚠️ Redis not available: {e}")
            print("   Falling back to SQLite")
            self.enabled = False
            self.fallback = StateManager()

    def save_request(
        self,
        request_id: str,
        state: Dict[str, Any],
        status: str = 'in_progress',
        **kwargs
    ):
        """Salva request no Redis"""
        if not self.enabled:
            return self.fallback.save_request(request_id, state, status, **kwargs)

        key = f"request:{request_id}"

        data = {
            'request_id': request_id,
            'status': status,
            'state': json.dumps(state, ensure_ascii=False),
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            **{k: json.dumps(v) if isinstance(v, dict) else str(v) for k, v in kwargs.items()}
        }

        # Salvar como hash
        self.redis.hset(key, mapping=data)

        # Definir TTL
        self.redis.expire(key, self.ttl)

        # Adicionar a índice por status
        self.redis.sadd(f"status:{status}", request_id)

    def get_request(self, request_id: str) -> Optional[Dict]:
        """Retorna request do Redis"""
        if not self.enabled:
            return self.fallback.get_request(request_id)

        key = f"request:{request_id}"
        data = self.redis.hgetall(key)

        if not data:
            return None

        return {
            'request_id': data['request_id'],
            'created_at': data['created_at'],
            'updated_at': data['updated_at'],
            'status': data['status'],
            'state': json.loads(data['state']),
            'result': json.loads(data.get('result', 'null')),
            'error': data.get('error'),
            'metadata': json.loads(data.get('metadata', 'null'))
        }

    def update_status(self, request_id: str, status: str, error: Optional[str] = None):
        """Atualiza status no Redis"""
        if not self.enabled:
            return self.fallback.update_status(request_id, status, error)

        key = f"request:{request_id}"

        # Remover de índice anterior
        old_status = self.redis.hget(key, 'status')
        if old_status:
            self.redis.srem(f"status:{old_status}", request_id)

        # Atualizar
        self.redis.hset(key, 'status', status)
        self.redis.hset(key, 'updated_at', datetime.utcnow().isoformat())

        if error:
            self.redis.hset(key, 'error', error)

        # Adicionar a novo índice
        self.redis.sadd(f"status:{status}", request_id)

    def list_requests(self, status: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Lista requests do Redis"""
        if not self.enabled:
            return self.fallback.list_requests(status, limit)

        if status:
            request_ids = list(self.redis.smembers(f"status:{status}"))[:limit]
        else:
            # Buscar todas as keys de requests
            request_ids = [
                key.split(':')[1]
                for key in self.redis.keys("request:*")
            ][:limit]

        results = []
        for request_id in request_ids:
            req = self.get_request(request_id)
            if req:
                results.append({
                    'request_id': req['request_id'],
                    'created_at': req['created_at'],
                    'updated_at': req['updated_at'],
                    'status': req['status']
                })

        return results


# ============================================================================
# SINGLETON (Global Instance)
# ============================================================================

# Por default usa SQLite (zero dependencies)
# Para produção, trocar para RedisStateManager
state_manager = StateManager()


def get_state_manager() -> StateManager:
    """Factory para obter state manager"""
    return state_manager
