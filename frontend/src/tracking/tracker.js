/**
 * 경로/명령을 분석·보관하는 순수 모델.
 * - addTelemetry({pos:{x,y,z}, ...}) 로 좌표 누적
 * - addCommand({action, direction, speed, ts?}) 로 명령 히스토리 기록
 * - getPath(): 최근 N개 좌표 반환
 * - getLast(): 최신 좌표 반환
 */
export class PathTrackerModel {
  constructor(maxPoints = 2000) {
    this.maxPoints = maxPoints;
    this.points = [];     // [{x,y,ts}]
    this.commands = [];   // [{action,direction,speed,ts}]
    this._version = 0;    // 외부 렌더 트리거용
  }

  addTelemetry(t) {
    const p = t?.pos;
    if (p && Number.isFinite(p.x) && Number.isFinite(p.y)) {
      this.points.push({ x: p.x, y: p.y, ts: Date.now() });
      if (this.points.length > this.maxPoints) {
        this.points.splice(0, this.points.length - this.maxPoints);
      }
      this._version++;
    }
  }

  addCommand(c) {
    const item = { ts: Date.now(), ...c };
    this.commands.push(item);
    // 필요하면 명령 기반 예측/스무딩 등을 여기서 수행 가능
    if (this.commands.length > this.maxPoints) {
      this.commands.splice(0, this.commands.length - this.maxPoints);
    }
    this._version++;
  }

  getPath(limit = 800) {
    if (this.points.length <= limit) return this.points.slice();
    return this.points.slice(this.points.length - limit);
  }

  getLast() {
    return this.points.length ? this.points[this.points.length - 1] : null;
  }

  get version() { return this._version; }
}
