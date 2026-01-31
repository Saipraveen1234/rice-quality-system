import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AnalysisService, AnalysisResult } from '../../services/analysis.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.html',
  styleUrls: ['./dashboard.css']
})
export class DashboardComponent implements OnInit {
  history: AnalysisResult[] = [];
  loading = true;

  totalInspections = 0;
  averageQuality = 0;
  averageBrokenGrains = 0;

  constructor(private analysisService: AnalysisService) { }

  ngOnInit() {
    this.analysisService.getHistory().subscribe({
      next: (data) => {
        this.history = data;
        this.calculateStats();
        this.loading = false;
      },
      error: () => this.loading = false
    });
  }

  calculateStats() {
    if (this.history.length === 0) {
      this.totalInspections = 0;
      this.averageQuality = 0;
      this.averageBrokenGrains = 0;
      return;
    }

    this.totalInspections = this.history.length;

    const totalQuality = this.history.reduce((sum, item) => sum + item.qualityScore, 0);
    this.averageQuality = Math.round(totalQuality / this.totalInspections);

    const totalBroken = this.history.reduce((sum, item) => sum + item.brokenGrains, 0);
    // Calculate average broken grains percentage or count. Let's do average count for now, 
    // but maybe percentage is better? The UI plan said "Recent Broken Grain Rate".
    // Let's stick to simple average count for now as per plan context, or better yet, calculate rate if total grains > 0.

    // Actually, let's just do average count as a safe bet from the data we have.
    this.averageBrokenGrains = Math.round(totalBroken / this.totalInspections);
  }
}
