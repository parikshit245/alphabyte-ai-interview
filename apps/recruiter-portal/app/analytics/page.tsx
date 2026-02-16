"use client";

import { Card, Metric, Text, DonutChart, LineChart } from "@tremor/react";

const performanceData = [
  { date: "2024-01", Score: 75 },
  { date: "2024-02", Score: 78 },
  { date: "2024-03", Score: 82 },
  { date: "2024-04", Score: 80 },
  { date: "2024-05", Score: 85 },
];

const stageData = [
  { name: "Applied", value: 45 },
  { name: "Screening", value: 28 },
  { name: "Interview", value: 15 },
  { name: "Offer", value: 8 },
  { name: "Hired", value: 4 },
];

export default function AnalyticsPage() {
  return (
    <div className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-8">Analytics</h1>

      <div className="grid md:grid-cols-3 gap-6 mb-8">
        <Card>
          <Text>Avg Interview Score</Text>
          <Metric>0</Metric>
        </Card>

        <Card>
          <Text>Success Rate</Text>
          <Metric>0%</Metric>
        </Card>

        <Card>
          <Text>Time to Hire</Text>
          <Metric>0 days</Metric>
        </Card>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <Card>
          <Text>Candidate Performance Trend</Text>
          <LineChart
            className="mt-4 h-72"
            data={performanceData}
            index="date"
            categories={["Score"]}
            colors={["blue"]}
          />
        </Card>

        <Card>
          <Text>Pipeline Distribution</Text>
          <DonutChart
            className="mt-4 h-72"
            data={stageData}
            category="value"
            index="name"
            colors={["blue", "cyan", "indigo", "violet", "purple"]}
          />
        </Card>
      </div>
    </div>
  );
}
