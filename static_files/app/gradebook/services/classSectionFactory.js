angular.module('gradeBookApp.services')
  .factory(
  'classSectionFactory',
  [
    'appConfig',
    '$resource',
    '$log',
    function (appConfig, $resource, $log){
      return $resource(appConfig.apiUrl + 'classSection/:sectionId/ ',
        {
          sectionId: '@sectionId'
        },
        {
          getBySection: {
            method: 'GET',
            interceptor: {
              responseError: function (error) {
                $log.error('GET USER LIST WITH ASSIGNMENTS:', error);
                return {
                  id: 1,
                  assignments: [
                    {
                      id:1,
                      name: 'Quiz',
                      weight: 25,
                      category: 1
                    },
                    {
                      id: 2,
                      name: 'Midterm',
                      weight: 50,
                      category: 2
                    },
                    {
                      id: 3,
                      name: 'Project',
                      weight:15,
                      category: 3
                    }
                  ],
                  users: [
                    {
                      id: 1,
                      firstName: 'Ashor',
                      lastName: 'Lior',
                      finalGrade: 0,
                      assignments: [
                        {
                          id: 1,
                          assignmentId:1,
                          value: 26
                        },
                        {
                          id:2,
                          assignmentId:2,
                          value: 35
                        },
                        {
                          id: 3,
                          assignmentId:3,
                          value: 57
                        }
                      ]
                    },
                    {
                      id: 2,
                      firstName: 'Lianna',
                      lastName: 'Congrains',
                      finalGrade: 0,
                      assignments: [
                        {
                          id:4,
                          assignmentId:1,
                          value: 15
                        },
                        {
                          id:5,
                          assignmentId:2,
                          value: 15
                        },
                        {
                          id: 6,
                          assignmentId:3,
                          value: 17
                        }
                      ]
                    },
                    {
                      id: 3,
                      firstName: 'Andy',
                      lastName: 'Dirkse',
                      finalGrade: 0,
                      assignments: [
                        {
                          id:7,
                          assignmentId:1,
                          value: 35
                        },
                        {
                          id:8,
                          assignmentId:2,
                          value: 55
                        },
                        {
                          id: 9,
                          assignmentId:3,
                          value: 58
                        }
                      ]
                    },

                    {
                      id: 5,
                      firstName: 'Jacob',
                      lastName: 'Hammer',
                      finalGrade: 0,
                      assignments: [
                        {
                          id:13,
                          assignmentId:1,
                          value: 26
                        },
                        {
                          id:14,
                          assignmentId:2,
                          value: 51
                        },
                        {
                          id: 15,
                          assignmentId:3,
                          value: 57
                        }
                      ]
                    },
                    {
                      id: 5,
                      firstName: 'Maria',
                      lastName: 'Hadrin',
                      finalGrade: 0,
                      assignments: [
                        {
                          id:10,
                          assignmentId:1,
                          value: 45
                        },
                        {
                          id:11,
                          assignmentId:2,
                          value: 75
                        },
                        {
                          id: 12,
                          assignmentId:3,
                          value: 87
                        }
                      ]
                    },
                    {
                      id: 6,
                      firstName: 'Salma',
                      lastName: 'Ortega',
                      finalGrade: 0,
                      assignments: [
                        {
                          id:10,
                          assignmentId:1,
                          value: 45
                        },
                        {
                          id:11,
                          assignmentId:2,
                          value: 75
                        },
                        {
                          id: 12,
                          assignmentId:3,
                          value: 87
                        }
                      ]
                    },
                    {
                      id: 14,
                      firstName: 'Vincent',
                      lastName: 'Rose',
                      finalGrade: 0,
                      assignments: [
                        {
                          id:10,
                          assignmentId:1,
                          value: 45
                        },
                        {
                          id:11,
                          assignmentId:2,
                          value: 75
                        },
                        {
                          id: 12,
                          assignmentId:3,
                          value: 87
                        }
                      ]
                    },
                    {
                      id: 24,
                      firstName: 'Allen',
                      lastName: 'West',
                      finalGrade: 0,
                      assignments: [
                        {
                          id:10,
                          assignmentId:1,
                          value: 45
                        },
                        {
                          id:11,
                          assignmentId:2,
                          value: 75
                        },
                        {
                          id: 12,
                          assignmentId:3,
                          value: 87
                        }
                      ]
                    }
                  ]
                }
              }
            }
          },
          get: {
            method: 'GET',
            isArray: true,
            interceptor: {
              responseError: function (error) {
                $log.error('GET CLASSES AND SECTIONS:', error);
                return [
                  {
                    name: 'Algebra II',
                    sections: [
                      {
                        id: 1,
                        name: 'Period 1'
                      },
                      {
                        id: 2,
                        name: 'Period 2'
                      },
                      {
                        id:3,
                        name: 'Period 3'
                      },
                      {
                        id: 4,
                        name: 'Period 4'
                      }
                    ]
                  },
                  {
                    name: 'Algebra I',
                    sections: [
                      {
                        id: 5,
                        name: 'Period 1'
                      },
                      {
                        id: 6,
                        name: 'Period 2'
                      }
                    ]
                  },
                  {
                    name: 'Geometry 10',
                    sections: [
                      {
                        id: 7,
                        name: 'Period 1'
                      },
                      {
                        id: 8,
                        name: 'Period 2'
                      }
                    ]
                  }
                ]
              }
            }
          }
        }
      )
    }
  ]
);
