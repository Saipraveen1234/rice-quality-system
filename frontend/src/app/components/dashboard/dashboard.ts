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

  constructor(private analysisService: AnalysisService) { }

  ngOnInit() {
    this.analysisService.getHistory().subscribe({
      next: (data) => {
        this.history = data;
        this.loading = false;
      },
      error: () => this.loading = false
    });
  }
}
