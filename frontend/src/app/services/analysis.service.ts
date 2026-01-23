import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface AnalysisResult {
    id: number;
    imageUrl: string;
    status: string;
    totalGrains: number;
    goodGrains: number;
    brokenGrains: number;
    qualityScore: number;
    createdAt: string;
}

@Injectable({
    providedIn: 'root'
})
export class AnalysisService {
    private apiUrl = 'http://localhost:3000/api';

    constructor(private http: HttpClient) { }

    uploadImage(file: File): Observable<AnalysisResult> {
        const formData = new FormData();
        formData.append('image', file);

        return this.http.post<AnalysisResult>(`${this.apiUrl}/analyze`, formData);
    }

    getHistory(): Observable<AnalysisResult[]> {
        return this.http.get<AnalysisResult[]>(`${this.apiUrl}/history`);
    }
}
